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
| Naive | `models/naive_model.py` | **Extracción exacta** de la celda 45 | Sí — bloque NAIVE dentro de `evaluar_serie()` |
| Naive + Tendencia | `models/naive_trend_model.py` | **Extracción exacta** de la celda 45 | Sí — bloque NAIVE TREND dentro de `evaluar_serie()` |
| AR (standalone) | `models/ar_model.py` | **Combinación nueva** — AR aplicado directo a la serie cruda | No — solo existe `seleccionar_ar_por_aic`/`forecast_ar_resid` (celda 60), siempre aplicado a un residuo STL, nunca a la serie cruda |
| Naive + Tendencia + Estacionalidad | `models/naive_trend_seasonal_model.py` | **Combinación nueva** — tendencia lineal + estacionalidad repetida, residuo=0 | No — la celda 64 tiene las piezas pero siempre acompañadas de un modelo de residuos |
| AR sobre residuos + Tendencia + Estacionalidad | `models/ar_resid_trend_seasonal_model.py` | **Combinación nueva** — tendencia+estacionalidad de la celda 64 + AR (celda 60) sobre el residuo | No — la combinación exacta (tendencia lineal simple + AR sobre residuo, sin LSTM de por medio) no existe; en la celda 60 la tendencia siempre la modela una LSTM |
| LSTM multivariada sobre residuos + Tendencia + Estacionalidad | `models/lstm_resid_model.py` | **Combinación nueva** — tendencia+estacionalidad de la celda 64 + arquitectura LSTM-por-componente de la celda 60 (retargeted a residuo) + catálogo/tratamiento de exógenas de la celda 58 | No — combina piezas de 3 celdas distintas (64, 60, 58) que nunca se combinaron así en el notebook |

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

## LightGBM — rediseño 2026-08-09 (smoke test FAIL → ventana de lags/rolling adaptativa)

El smoke test de LightGBM falló en Colab (commit `041a3c0`) contra el pipeline descrito arriba. Causa raíz, encontrada leyendo `create_feature_df`: tanto el bloque de lags (`lag_1..lag_window`) como las columnas `rolling_mean_168`/`rolling_std_168` usaban una ventana de **168h fija**, copiada de XGBoost, sin relación con `train_hours`/`forecast_horizon`. Con el propio default vigente (`train_hours=336`, `forecast_horizon=168`), el presupuesto de filas que ve cada trial de Optuna durante el tuning es `train_hours - forecast_horizon = 168` filas — exactamente igual a la ventana — así que `.dropna()` vaciaba el DataFrame en **todos** los trials, cada uno retornaba `inf` silenciosamente (sin excepción) y el tuning nunca comparó hiperparámetros de verdad; solo el ajuste final (que sí usa el `train_hours` completo) producía un modelo real, con hiperparámetros esencialmente arbitrarios. Con un `train_hours` más chico (como en el smoke test, pensado para correr rápido), incluso el ajuste final se quedaba sin filas: la región terminaba sin ninguna métrica, sin lanzar ninguna excepción tampoco — un fallo completamente silencioso.

Corrección (aplicada solo a LightGBM, no a XGBoost): `_resolver_window(train_hours, forecast_horizon)` deriva la ventana del presupuesto real de filas (`(train_hours - forecast_horizon) // 2`), con piso de 24h y techo de 168h; `create_feature_df`/`create_features_from_history` usan esa misma ventana tanto para los lags como para el rolling "largo" (renombrado `rolling_mean_larga`/`rolling_std_larga`, ya no sugiere un número de horas fijo que dejó de aplicar). Verificado empíricamente (no solo por inspección) que con el default vigente esto da `window=84` y dobla el tuning en algo funcional (84 filas ≥ el umbral de 50 filas mínimas para no retornar `inf`); con presupuestos grandes el `window` sube hasta el mismo techo de 168h que usa XGBoost. `tests/smoke_lightgbm.py` se re-dimensionó (`train_hours=200`, `forecast_horizon=48`) para ejercitar el caso adaptativo real en vez del caso que crasheaba.

## Diferencias científicas reales entre modelos (por qué no se comparte código)

Verificadas leyendo el código fuente exacto de cada celda, no asumidas:

- **Métricas (`mape`/`smape`/`calcular_metricas`) NO son idénticas entre modelos.** XGBoost/LightGBM no tienen máscara `isfinite` y `calcular_metricas` devuelve `None` si está vacío. LSTM directa también devuelve `None` pero SÍ enmascara con `isfinite`. SARIMAX enmascara con `isfinite` pero devuelve un dict de `NaN` (no `None`) si está vacío. FCNN igual que SARIMAX. Ensemble enmascara con `isfinite` pero **no tiene guarda contra vacío** (lanzaría una excepción). Por esto cada módulo tiene su propia copia — `metrics.py` compartido solo lo usan XGBoost y LightGBM (verificado carácter por carácter que ahí sí son idénticas).
- **Tratamiento de exógenas futuras no conocidas** (Generación/Importación/Exportación): XGBoost/LightGBM/SARIMAX usan **promedio de dos lags** (t-168 y t-336). LSTM directa usa **un solo lag** de t-168. FCNN/Ensemble usan un mecanismo distinto: la exógena se pre-desplaza 168h en la construcción de la matriz (`preparar_exogena_lag168`, corriendo el timestamp) y luego se trata como si fuera contemporánea.
- **Objetivo de tuning de Optuna**: XGBoost/LightGBM/LSTM directa/FCNN optimizan **sMAPE**. Los submodelos LSTM(tendencia) y FCNN(estacionalidad) dentro de Ensemble optimizan **MAE**.
- **Arquitectura LSTM**: `lstm_direct.py` usa secuencias reales `(window, features)` con salida `Dense(168)` en una sola pasada (multi-horizonte directo). El LSTM dentro de `ensemble_stl.py` es estructuralmente distinto: aplana la ventana en un vector y le da forma `(1, features)` — un solo timestep pseudo-secuencial, 1 o 2 capas — y pronostica recursivamente paso a paso. No comparten arquitectura pese a llamarse igual.
- **Resume de Optuna**: XGBoost/LightGBM/LSTM directa/SARIMAX(N/A, sin tuning) simplemente llaman `study.optimize(n_trials=N)` cada vez. FCNN y Ensemble cuentan trials ya completados en el estudio y solo corren `N - completados` — un mecanismo de resume real, distinto entre familias de modelos.
- **Tolerancia a fallos por región**: LSTM directa envuelve la región completa (carga + evaluación + guardado) en un único `try/except`. XGBoost solo protege la evaluación del modelo, no la carga de exógenas. SARIMAX/FCNN/Ensemble protegen tanto la construcción de exógenas como la evaluación, cada uno con su propia estructura de niveles anidados.

Ningún cambio de este proyecto intentó unificar nada de lo anterior — se preservó cada comportamiento tal cual estaba en su celda de origen.

## FCNN — corrección quirúrgica 2026-08-09 (smoke test FAIL → construcción de series.csv)

El smoke test de FCNN falló en Colab (commit `041a3c0`) con `ValueError: If using all scalar values, you must pass an index` al construir el DataFrame final de series, aunque ambos modelos (directa y STL-residuos) entrenaban y producían métricas válidas. Causa raíz: `resultados.series` mezcla dos formas de bloque — una fila por cada predicción (valores escalares, vía `_guardar_bloque`) y un bloque "real" por región con `fecha`/`valor` como arreglo completo de la serie (array, no escalar). La agregación final (`for bloque in resultados.series: pd.DataFrame({...})`) construía cada bloque directamente; para los bloques de predicción, con TODOS los valores del dict escalares, `pd.DataFrame({...})` exige un índice explícito y lanza esa excepción. El guardado incremental (`_guardar_avance_csv`) tenía un bug relacionado pero silencioso: `pd.DataFrame(resultados.series)` trataba cada bloque como una sola fila, así que el bloque "real" (con arreglo) habría quedado mal serializado (una fila con una celda conteniendo un arreglo) en vez de expandirse a una fila por hora — nunca se manifestó como excepción porque el guardado final (correcto en la agregación final antes del fix) sobrescribía ese archivo intermedio al terminar.

Corrección quirúrgica: nueva función `_construir_df_series()` que envuelve `fecha`/`valor` con `np.atleast_1d(...)` antes de construir cada bloque — normaliza escalares a arreglos de 1 elemento sin tocar ningún valor ni el orden de las filas, y pandas hace el broadcast correctamente en ambos casos (fila única o serie completa). Se usa en los dos lugares que antes tenían el problema (`_guardar_avance_csv` y la agregación final de `run()`), eliminando también el bug silencioso del guardado incremental. Ningún cambio en arquitectura, tuning, exógenas, train/test ni métricas.

## Modelos nuevos: combinaciones, NO extracciones (2026-08-09)

Cuatro modelos pedidos explícitamente por el usuario no existen como pipeline completo en el notebook legacy, sino solo como piezas sueltas (funciones reutilizables) en distintas celdas. El usuario confirmó exactamente qué combinar y con qué metodología, y pidió que quedara documentado con claridad que **son combinaciones nuevas, no extracciones fieles** — a diferencia de todo lo demás en este documento.

### AR (standalone) — `models/ar_model.py`

Reutiliza `seleccionar_ar_por_aic`/`forecast_ar_resid` de la celda 60 (barrido de lags 1-168 por AIC, `AutoReg(trend="c")`) pero aplicado **directo a la serie cruda de Demanda**, sin ninguna descomposición STL. En la celda 60 esa función SIEMPRE se aplica a un residuo STL — nunca a la serie cruda. Univariado, split dinámico igual a `naive_model.py` (`test_size = max(720h, 10%)`, acotado a `len//3`), métricas del `metrics.py` compartido (misma familia que XGBoost/Naive/Naive_Trend). `trials.csv` es el barrido de lags (no trials de Optuna); `config_usada.csv` registra el lag óptimo.

### Naive + Tendencia + Estacionalidad — `models/naive_trend_seasonal_model.py`

Reutiliza `descomponer_stl`/`forecast_tendencia_lineal`/`forecast_estacionalidad_repetida` de la celda 64 **tal cual**, pero sin ningún modelo de residuo (`residuo = 0`): `pred_final = tendencia + estacionalidad`. En la celda 64 esas tres funciones siempre van acompañadas de un modelo de residuo (FCNN); esta combinación —tendencia+estacionalidad sola, sin residuo— no existe en legacy. Univariado, ventana FIJA 3600h/168h (no la fórmula dinámica de Naive/AR — STL con `period=168` necesita una ventana larga y estable), métricas de la familia celda-64 (`isfinite` + guarda contra vacío). Sin tuning.

### AR sobre residuos + Tendencia + Estacionalidad — `models/ar_resid_trend_seasonal_model.py`

Extiende el modelo anterior: mismas `descomponer_stl`/`forecast_tendencia_lineal`/`forecast_estacionalidad_repetida` de la celda 64, más `seleccionar_ar_por_aic` de la celda 60 aplicado al **residuo STL** (no a la serie cruda, a diferencia de `ar_model.py`). `pred_final = tendencia + estacionalidad + AR(residuo)`. Esta combinación tampoco existe en legacy: en la celda 60 la tendencia siempre la modela una LSTM tuneada con Optuna, nunca una regresión lineal simple. Univariado, misma ventana fija 3600h/168h que el modelo anterior (consistencia dentro de la familia STL), misma familia de métricas. `trials.csv` es el barrido de lags sobre el residuo.

### LSTM multivariada sobre residuos + Tendencia + Estacionalidad — `models/lstm_resid_model.py`

La combinación más compleja de las cuatro: combina piezas de **tres** celdas distintas.
1. Tendencia + estacionalidad: copia exacta de la celda 64 (igual que los dos modelos anteriores).
2. Modelo del residuo: la arquitectura LSTM-por-componente-STL de la celda 60 (`crear_ventanas`, `reshape_lstm_features`, `construir_lstm`, `tunear_lstm`, `entrenar_lstm_final`, `forecast_recursivo_lstm`) — en el Ensemble original esa arquitectura modela la TENDENCIA; aquí se retargetea al RESIDUO (funciones genéricas, no requirieron cambios).
3. Catálogo y tratamiento de exógenas: copia exacta de la celda 58 (LSTM directa) — `EXOG_COLS_DEFAULT`, `EXOG_SOURCE_MAP`, `EXOG_CONOCIDAS_FUTURO`/`EXOG_LAG_SEMANAL`, `LAG_EXOG_FUTURO=168`, `merge_exogenas`, `alinear_exogenas_a_fechas`, `construir_future_exog_directa` — **no** el tratamiento propio del Ensemble (`preparar_exogena_lag168`, que desplaza el timestamp). Esta sustitución fue instruida explícitamente por el usuario: "usa el mismo conjunto y tratamiento de exógenas que la LSTM multivariada vigente".

`pred_final = tendencia + estacionalidad + LSTM(residuo)`. Único de los cuatro que SÍ requiere exógenas (es multivariado). Ventana fija 3600h/168h, `WINDOW=168` para la LSTM (igual que Ensemble), `N_TRIALS_DEFAULT=5` (heredado de Ensemble, no el 10 de LSTM directa — la maquinaria de tuning que se reutiliza es la del Ensemble). Métricas de la familia celda-64, igual que los dos modelos anteriores. No incluye filas `componente_pred` separadas en `series.csv` (a diferencia de Ensemble) — solo `real` y la predicción final combinada, por consistencia con los otros dos modelos nuevos de esta familia.

**Limitación conocida:** requiere `tensorflow` y `optuna`, ninguno instalado en el entorno de desarrollo local. No se pudo correr un smoke test real end-to-end localmente (a diferencia de los otros tres modelos nuevos). Sí se verificó por separado, con pandas/numpy/statsmodels/sklearn puros (sin tensorflow/optuna), toda la lógica que no depende de esas librerías: extracción de serie, construcción y alineación de exógenas, tratamiento futuro (conocida vs. lag168) verificado valor-por-valor, descomposición STL, y las dimensiones exactas de las ventanas que vería la LSTM (`crear_ventanas`). Debe correrse el smoke test real en Colab antes de confiar en el pipeline completo.

## Smoke tests

Uno por modelo en `tests/`, mismo patrón: construyen datos sintéticos mínimos (1 región, ventanas chicas, 1 trial de Optuna donde aplica) y corren el pipeline `run()` completo de punta a punta, verificando shapes, ausencia de NaN inesperado, y que se generen los archivos esperados.

| Smoke test | Ejecutado en este entorno | Resultado |
|---|---|---|
| `tests/smoke_sarimax.py` | **Sí** (solo depende de statsmodels/sklearn, disponibles localmente) | OK — corrida real, MAPE=1.59% sobre datos sintéticos, re-verificado 2026-08-09 sin cambios |
| `tests/smoke_lightgbm.py` | No (falta `lightgbm`/`optuna` en este entorno). Re-dimensionado (`train_hours=200`, `forecast_horizon=48`) y la lógica de `_resolver_window`/`create_feature_df` verificada por separado con pandas/numpy puro (sin lightgbm/optuna), reproduciendo el conteo de filas exacto que vería el pipeline real. | FAIL en Colab (commit `041a3c0`) → corregido, pendiente de re-correr en Colab |
| `tests/smoke_lstm_direct.py` | No (falta `tensorflow`/`optuna`) | PASS en Colab (commit `041a3c0`), sin cambios en este módulo |
| `tests/smoke_fcnn.py` | No (falta `tensorflow`/`optuna`). El bug de `_construir_df_series` fue reproducido y verificado corregido con pandas/numpy puro, aislado del resto del pipeline. | FAIL en Colab (commit `041a3c0`) → corregido, pendiente de re-correr en Colab |
| `tests/smoke_ensemble_stl.py` | No (falta `tensorflow`/`optuna`) | PASS en Colab (commit `041a3c0`), sin cambios en este módulo |
| `tests/smoke_ar.py` | **Sí** (solo depende de statsmodels/sklearn) | OK — corrida real, MAPE=1.83%, lag óptimo=168 |
| `tests/smoke_naive_trend_seasonal.py` | **Sí** (solo depende de statsmodels/sklearn) | OK — corrida real, MAPE=0.81% |
| `tests/smoke_ar_resid_trend_seasonal.py` | **Sí** (solo depende de statsmodels/sklearn) | OK — corrida real, MAPE=0.85%, lag óptimo residuo=168 |
| `tests/smoke_lstm_resid.py` | No (falta `tensorflow`/`optuna`). Lógica sin esas librerías (extracción de serie, alineación de exógenas, tratamiento futuro conocida/lag168, STL, dimensiones de ventanas) verificada por separado con pandas/numpy/statsmodels/sklearn puros. | Pendiente de correr en Colab |

Todos compilan (`py_compile`) y su lógica de generación de datos sintéticos fue verificada por separado donde no dependía de las librerías faltantes.
