# Estado de migración de modelos al sistema nuevo

Fuente de verdad de qué modelo es qué tipo de migración. Ver también
`docs/AUTOMATIZACION_FUTURA.md` (compatibilidad con cola/matriz) y el
checklist de equivalencia entregado con la migración de XGBoost (en el
historial de la conversación) para el detalle exacto celda-por-celda.

| Modelo | Módulo | Tipo de migración | Pipeline vigente en legacy |
|---|---|---|---|
| XGBoost | `models/xgboost_model.py` | **Extracción exacta** de la celda 49 | Sí — sección dedicada "Ahora sí multivariado a 1 semana XGBoost", validada corriendo en Colab |
| LightGBM | `models/lightgbm_model.py` | **Adaptado / estandarizado** desde la celda 46 (prototipo legacy) | **No** — no existe una sección vigente dedicada, solo aparecía embebido en la celda 46 junto con Naive/XGBoost/LSTM |
| LSTM directa multi-horizonte | `models/lstm_direct.py` | **Extracción exacta** de la celda 58 ("LSTM pero con 60 épocas y más Optuna") | Sí — la celda 55 ("LSTM: No funcionó!") es la versión legacy/fallida, NO se migró |
| SARIMAX | `models/sarimax_model.py` | **Extracción exacta** de la celda 62 | Sí — orden fijo (1,1,1)(1,0,1,168), sin tuning |
| FCNN multivariada | `models/fcnn_model.py` | **Extracción exacta** de la celda 64 | Sí — incluye las 2 estrategias originales: directa y STL-residuos |
| Ensemble STL | `models/ensemble_stl.py` | **Extracción exacta** de la celda 60 | Sí — STL + LSTM(tendencia) + FCNN(estacionalidad) + AR(residuo), arquitectura conservada tal cual, no se convirtió en ensamble de los otros modelos ya migrados |

Los 4 extraídos el 2026-08-08 comparten con XGBoost/LightGBM el mismo patrón mecánico de adaptación: `globals()`/diccionario `series` → `exogenas_globales` (parámetro) + lectura de `{region}_GEN/IMP/EXP.csv` desde `data_dir`; script de nivel de módulo o `ejecutar_pipeline()` → `run(...)`; listas de resultados globales → acumulador local; `OUTPUT_DIR` fijo → `output_dir`. Ver el docstring de cada módulo para el detalle exacto de qué se preservó literal y qué es adaptación mecánica (no científica).

## LightGBM — qué es exactamente "adaptado/estandarizado"

**No leas `lightgbm_model.py` esperando que sea fiel a una celda del notebook legacy como los demás.** Es una construcción nueva que combina:

**Tomado literalmente de la celda 46** (líneas 403-415, `objective_lightgbm`):
- Espacio de búsqueda de Optuna: `n_estimators[50,200]`, `max_depth[2,8]`, `learning_rate[0.03,0.25]`, `num_leaves[16,80]`, `subsample[0.7,1]`, `colsample_bytree[0.7,1]`, `reg_alpha/reg_lambda[0,5]`, `random_state=42`, `verbose=-1`.
- Uso de `LGBMRegressor`.
- `N_TRIALS_OPTUNA=10` y `WINDOW=168` (coinciden por casualidad con los defaults de XGBoost, pero vienen de la celda 46).

**NO tomado de la celda 46, adaptado para igualar el marco vigente de XGBoost** (por instrucción explícita del usuario, 2026-08-08):
- Ventana train/test fija (default 336h/168h) — la celda 46 usaba un esquema de porcentaje de la serie completa (`test_size = max(24*30, 10%)`) con validación de 3 splits y gap de 168h.
- Catálogo completo de 8 exógenas (`Temperatura, Primarias, Secundarias, Terciarias, IGAE, Generacion, Importacion, Exportacion`) — la celda 46 solo tenía las 5 globales, sin las 3 eléctricas por región.
- Tratamiento futuro conocido/estimado (Temp/IGAE = valor real, resto = promedio t-168/t-336) — la celda 46 no distinguía esto, usaba el valor de `future_exog` tal cual para todas.
- Construcción de features por lags + rolling stats, **sin** las features de calendario (hour/dayofweek/month seno-coseno) que sí tenía `create_feature_df_multivar` en la celda 46 — se priorizó consistencia con XGBoost sobre replicar ese detalle.
- Todo el andamiaje de guardado/RUN_NAME/`ExperimentResult`/logs — no existía nada de esto en la celda 46.

**Consecuencia práctica:** los resultados de `lightgbm_model.py` **no son directamente comparables** con ninguna corrida legacy de LightGBM (esa corrida nunca existió con este framework). Sí son comparables con las corridas de XGBoost del sistema nuevo, que es el objetivo que se pidió.

## Diferencias científicas reales entre modelos (por qué no se comparte código)

Verificadas leyendo el código fuente exacto de cada celda, no asumidas:

- **Métricas (`mape`/`smape`/`calcular_metricas`) NO son idénticas entre modelos.** XGBoost/LightGBM no tienen máscara `isfinite` y `calcular_metricas` devuelve `None` si está vacío. LSTM directa también devuelve `None` pero SÍ enmascara con `isfinite`. SARIMAX enmascara con `isfinite` pero devuelve un dict de `NaN` (no `None`) si está vacío. FCNN igual que SARIMAX. Ensemble enmascara con `isfinite` pero **no tiene guarda contra vacío** (lanzaría una excepción). Por esto cada módulo tiene su propia copia — `metrics.py` compartido solo lo usan XGBoost y LightGBM (verificado carácter por carácter que ahí sí son idénticas).
- **Tratamiento de exógenas futuras no conocidas** (Generación/Importación/Exportación): XGBoost/LightGBM/SARIMAX usan **promedio de dos lags** (t-168 y t-336). LSTM directa usa **un solo lag** de t-168. FCNN/Ensemble usan un mecanismo distinto: la exógena se pre-desplaza 168h en la construcción de la matriz (`preparar_exogena_lag168`, corriendo el timestamp) y luego se trata como si fuera contemporánea.
- **Objetivo de tuning de Optuna**: XGBoost/LightGBM/LSTM directa/FCNN optimizan **sMAPE**. Los submodelos LSTM(tendencia) y FCNN(estacionalidad) dentro de Ensemble optimizan **MAE**.
- **Arquitectura LSTM**: `lstm_direct.py` usa secuencias reales `(window, features)` con salida `Dense(168)` en una sola pasada (multi-horizonte directo). El LSTM dentro de `ensemble_stl.py` es estructuralmente distinto: aplana la ventana en un vector y le da forma `(1, features)` — un solo timestep pseudo-secuencial, 1 o 2 capas — y pronostica recursivamente paso a paso. No comparten arquitectura pese a llamarse igual.
- **Resume de Optuna**: XGBoost/LightGBM/LSTM directa/SARIMAX(N/A, sin tuning) simplemente llaman `study.optimize(n_trials=N)` cada vez. FCNN y Ensemble cuentan trials ya completados en el estudio y solo corren `N - completados` — un mecanismo de resume real, distinto entre familias de modelos.
- **Tolerancia a fallos por región**: LSTM directa envuelve la región completa (carga + evaluación + guardado) en un único `try/except`. XGBoost solo protege la evaluación del modelo, no la carga de exógenas. SARIMAX/FCNN/Ensemble protegen tanto la construcción de exógenas como la evaluación, cada uno con su propia estructura de niveles anidados.

Ningún cambio de este proyecto intentó unificar nada de lo anterior — se preservó cada comportamiento tal cual estaba en su celda de origen.

## Smoke tests

Uno por modelo en `tests/`, mismo patrón: construyen datos sintéticos mínimos (1 región, ventanas chicas, 1 trial de Optuna donde aplica) y corren el pipeline `run()` completo de punta a punta, verificando shapes, ausencia de NaN inesperado, y que se generen los archivos esperados.

| Smoke test | Ejecutado en este entorno | Resultado |
|---|---|---|
| `tests/smoke_sarimax.py` | **Sí** (solo depende de statsmodels/sklearn, disponibles localmente) | OK — corrida real, MAPE=1.59% sobre datos sintéticos |
| `tests/smoke_lightgbm.py` | No (falta `lightgbm`/`optuna` en este entorno) | Pendiente de correr en Colab |
| `tests/smoke_lstm_direct.py` | No (falta `tensorflow`/`optuna`) | Pendiente de correr en Colab |
| `tests/smoke_fcnn.py` | No (falta `tensorflow`/`optuna`) | Pendiente de correr en Colab |
| `tests/smoke_ensemble_stl.py` | No (falta `tensorflow`/`optuna`) | Pendiente de correr en Colab |

Todos compilan (`py_compile`) y su lógica de generación de datos sintéticos fue verificada por separado donde no dependía de las librerías faltantes.
