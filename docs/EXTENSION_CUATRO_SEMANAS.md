# Extension experimental a cuatro semanas de prueba

Ventanas de 168 h, todas con entrenamiento y seleccion de hiperparametros
estrictamente anteriores al inicio de la prueba:

| Id | Prueba (00:00 del primer dia a 23:00 del ultimo) |
|----|---|
| S1 | 26 abr - 2 may 2026 |
| S2 | 3 - 9 may 2026 |
| S3 | 10 - 16 may 2026 |
| S4 | 17 - 23 may 2026 (semana original de la tesis) |

## Como funciona (cambio minimo, ningun modelo tocado)

Todos los modelos toman como prueba las **ultimas `forecast_horizon` filas** de
`{REGION}_long.csv` y como entrenamiento las `train_hours` filas anteriores
(`xgboost_model._preparar_serie`, `*_model.run`). La semana la fija el final de
los datos. En lugar de reescribir 12 modelos, `windows.py` materializa, por
semana, un directorio con los datos **hasta el ultimo dia de la ventana**
(`{REGION}_long.csv` y `{REGION}_{GEN,IMP,EXP}.csv` con `fecha <= fin`; las dos
exogenas globales se copian sin cambios). El modelo recibe ese directorio
como `data_dir` y no puede ver nada posterior.

| Archivo | Cambio |
|---|---|
| `src/tesis_forecast/windows.py` (nuevo) | Definicion de S1-S4, materializacion de datos, diagnostico de cobertura. Sin librerias pesadas. |
| `config.py` | `ExperimentConfig.ventana` (default `None`). Con ventana, `config.json` registra `ventana`, `test_start`, `test_end`. Sin ventana nada cambia. |
| `io_drive.py` | `BASE_DIR_VENTANAS` y `resolve_ventanas_base_dir()`. |
| `runner.py` | Con `ventana`: carpeta `Pipeline_Resultados_Ventanas/<S#>/<RUN_NAME>`, exige horizonte 168 h, materializa los datos, guarda `ventana_manifest.json` en la corrida, omite (con aviso) regiones sin datos suficientes. |
| `matrix.py` | `MatrixRunRecord.duracion_s` y columnas `duracion_s`/`ventana` en `resumen_dataframe()` (tiempos por corrida). |
| `ventanas_tools.py` (nuevo) | Auditoria de datos, plan por niveles de costo, comparacion S4 vs original, consolidado, registro de tiempos. |
| `notebooks/run_ventanas.ipynb` (nuevo) | Flujo completo para Colab. |
| `scripts/run_local_estadisticos.py` (nuevo) | Corre localmente los 6 modelos estadisticos (sin TensorFlow/Optuna). |
| `tests/test_windows.py`, `tests/test_ventanas_tools.py` (nuevos) | Pruebas con datos sinteticos (locales, sin TensorFlow). |
| `docs/plan_corridas_ventanas.csv` | Las 216 corridas planeadas (ventana, nivel, modelo, exogenas, train_hours, RUN_NAME). |

El `RUN_NAME` no cambia con la ventana: la separacion es por **carpeta**
(`Pipeline_Resultados_Ventanas/S1/`, `.../S2/`, ...). Como cada estudio Optuna
vive en un `.db` dentro de la carpeta de su corrida (`output_dir`), los estudios
quedan separados por semana y `load_if_exists=True` nunca reutiliza trials de
otra semana. `Pipeline_Resultados/` (originales) no se escribe nunca desde una
corrida con ventana.

## Verificacion de no-fuga

| Punto | Resultado | Como se establecio |
|---|---|---|
| Demanda y GEN/IMP/EXP posteriores al fin de la prueba | **No existen** para el modelo | Estructural (`windows.materializar_datos_ventana`). `tests/test_windows.py` seccion 4: dos datasets identicos hasta el fin de S1 y con el futuro multiplicado x10 dan metricas y series **identicas** en S1. |
| Normalizacion (`StandardScaler`) | Solo con train (o train menos validacion durante el tuning) | Auditoria de codigo: `lstm_direct`, `lstm_resid_model`, `ensemble_stl`, `fcnn_model`. |
| STL | Solo sobre `train` | `descomponer_stl(train)` en `fcnn_model`, `ensemble_stl`, `lstm_resid_model`, `naive_trend_seasonal_model`, `ar_resid_trend_seasonal_model`; `train = serie[:-forecast_horizon]`. |
| Validacion / Optuna | Ultimas 168 h **del train**; la prueba nunca entra | `xgboost_model._preparar_serie` (`tune_train_y = train[:-val_size]`, `tune_val_y = train[-val_size:]`); exogenas de validacion tambien sin ver el futuro. LightGBM comparte el esquema. |
| Exogenas "futuras" no conocidas (Gen/Imp/Exp) | Solo valores de t-168 / t-336 (o desplazamiento de 168 h) | Anteriores al inicio de la prueba, por construccion. |
| Temperatura/IGAE/Primarias/Secundarias/Terciarias | Sin fuga posible: terminan el 31-mar-2026, antes de las cuatro pruebas | `data/exogenas.py` y auditoria de datos (ver abajo). |

## Decision metodologica: fecha de corte de las exogenas globales

Se **conserva** la metodologia original. `FECHA_CORTE_FIN = "2026-03-01"`
(`data/exogenas.py`) se fijo deliberadamente como **limite comun de informacion
exogena**, para evitar ventajas informativas entre configuraciones; marzo no
tiene relevancia por si mismo. Las cinco series globales (Temperatura, IGAE,
Primarias, Secundarias, Terciarias) son mensuales, se recortan a meses <= marzo de
2026 y se expanden a horas repitiendo el valor mensual (el ultimo dato horario
es el 31-mar-2026). Despues del corte `merge_exogenas` / `alinear_exogenas_*`
aplican `ffill`, de modo que desde el 1-abr-2026 esas cinco series son una
constante.

**Limitacion documentada.** Como las cuatro ventanas (26-abr a 23-may) son
posteriores al corte, en todas ellas las cinco series permanecen constantes por
forward fill (26, 33, 40 y 47 dias sin dato real antes de S1, S2, S3 y S4). Esto
implica: (a) que ninguna configuracion tiene ventaja informativa sobre otra por
esas variables y no hay fuga posible por ellas; (b) que en la prueba (y, para los
modelos con entrenamiento corto, tambien en las ultimas semanas de entrenamiento)
esas variables no aportan variacion. En particular, XGBoost/LightGBM entrenan con
336 h (14 dias) y esas columnas son constantes en todo su entrenamiento, lo que
es consistente con las metricas identicas entre configuraciones de exogenas que
reporta la tesis. La decision no se modifica; queda registrada para la discusion
de resultados. (Dato verificable en los archivos: la serie del IGAE de INEGI
termina en marzo de 2026 -- "Serie de enero de 1993 a marzo de 2026" -- y la
serie de temperatura termina en `mar-26`.)

## Auditoria de datos reales (copias locales)

Hecha el 2026-10-17 sobre copias locales de los archivos (listas de MD5 en
`docs/datos_locales_MD5SUMS.txt` para compararlas con las de Drive). **Falta
confirmar que las copias de Drive son identicas** (celda de auditoria de
`run_ventanas.ipynb`).

| Hallazgo | Detalle |
|---|---|
| Cobertura de la demanda | Las 8 regiones (BCA incluida): 2019-01-01 a 2026-05-23, 2 700 dias y 64 800 registros horarios por region (BCA: 64 799), sin NaN en la demanda. Las cuatro semanas estan completas (168 h unicas) y todas las regiones tienen historia de sobra para 336/1440/2160/3600 h. |
| Horario de verano | Los registros siguen la hora local: hay dias de 23 h (cambio de primavera) y de 25 h (otono, `Hora` llega a 25). Regiones peninsulares/centrales: 4 cambios (2019-2022). BCA: 8 dias de 23 h y 7 de 25 h (2019-2026). Ningun cambio cae dentro de las ventanas de prueba. En BCA, el cambio del 8-mar-2026 (dia de 23 h) cae dentro del entrenamiento de los modelos de 3600 h en las cuatro semanas; en las demas regiones no hay cambios desde 2022. |
| Generacion | Completa (2019-01-01 a 2026-05-23, sin NaN). |
| **Importacion y exportacion** | **Los archivos `*_IMP.csv` y `*_EXP.csv` solo tienen valor real en 2019** (8 759 filas no nulas de ~64 800; ultima fecha con valor: 2019-12-31). Provienen de las columnas `Flujo Real de Importacion/Exportacion (MWh)`, que en la fuente solo existen en 2019 (de 2020 en adelante la fuente trae `Importacion Total` / `Exportacion Total`, que no se extrajeron). Como `_normalizar_exogena` descarta las filas NaN y luego `merge_exogenas` aplica `ffill().bfill()`, **Importacion y Exportacion son constantes (el ultimo valor de 2019) en todo 2020-2026**, incluidas las cuatro pruebas y todo su entrenamiento. Esto **no se modifico**; debe decidirse como tratarlo antes de interpretar el efecto de estas dos variables. |
| Exogenas globales | Temperatura, IGAE, Primarias, Secundarias, Terciarias: ultimo dato real 2026-03-31. |
| `drop_every_13th` | **Resuelto**: la hoja del IGAE de INEGI trae, tras cada ano, una columna `Anual` (posiciones 13, 26, 39, 52...); la funcion elimina esos totales anuales para dejar solo los meses. |

## Reproduccion local de S4 con datos reales (2026-10-17)

Los modelos estadisticos no necesitan TensorFlow/Optuna y se corrieron aqui
(`scripts/run_local_estadisticos.py`) sobre las copias locales de los datos.
Como los originales de `Pipeline_Resultados/` viven en Drive, se compara contra
las tablas de la tesis y contra `Legacy_Univariados`.

| Modelo (S4, 3600 h / 168 h) | Referencia | Resultado |
|---|---|---|
| Naive | Tabla 5.2 (7 regiones) | **Coincide exactamente** en las 7 regiones |
| Naive + Tendencia | Tabla 5.2 | **Coincide exactamente** en las 7 regiones |
| AR por AIC | `Legacy_Univariados` `AR_AIC` (y media 5.84 de la Tabla 6.4) | **Coincide** en las 7 regiones |
| AR sobre residuos STL | `Legacy_Univariados` `STL_AR_residuos_AIC` (media 5.41, Tabla 6.4) | **Coincide** en las 7 regiones |
| Naive + Tendencia + Estacionalidad | Tabla 5.2, 3.a columna | **NO coincide**: CEN 2.21 (tesis 2.83), NES 6.97 (6.71), NOR 4.70 (9.62), NTE 5.49 (5.22), OCC 2.28 (2.42), ORI 5.39 (6.11), PEN 9.21 (5.08) |
| BCA, 384 h: ARIMA, SARIMA, AR, STL+AR | Tabla 6.5 | **Coincide exactamente** (37.37 / 4.12 / 15.19 / 26.19 % de MAPE) |

Conclusiones que se pueden respaldar:

1. Las copias locales de `_long.csv` son los datos con los que se produjeron esas
   tablas (al menos las ultimas 3600 h de cada region). Falta confirmar que las de
   Drive son identicas (MD5).
2. El script legacy univariado usaba, para `AR_AIC` y `STL_AR_residuos_AIC`, la
   misma ventana que el pipeline moderno (3600 h de entrenamiento, 168 h de
   prueba, semana S4). Eso hace plausible que la configuracion de 3600 h de la
   Tabla 5.13 (LSTM individual) tambien describa ese script, aunque su LSTM no se
   puede reproducir sin el codigo perdido.
3. **Tabla 5.2, columna "Naive+Trend+Seasonal", no sale de este codigo** con la
   ventana S4. Hay que compararla con `Naive_Trend_Seasonal_train3600h_fh168h`
   de `Pipeline_Resultados/` (celda 3 de `run_ventanas.ipynb`) para saber si la
   tabla se tomo de otra corrida (por ejemplo la del "desplazamiento de 1 h").
4. **BCA no tiene una restriccion de disponibilidad**: el archivo local tiene
   historia completa desde 2019 y, aun asi, los resultados con 384 h coinciden con
   la Tabla 6.5. La frase de la tesis ("se utilizaron 384 horas debido a la
   disponibilidad de la serie") no se sostiene con estos datos; si la serie de Drive
   fuera mas corta, las cifras no coincidirian. Confirmar con el MD5 de Drive.
5. SARIMAX (lento: SARIMA estacional de 168 h con 5 exogenas) esta corriendo
   localmente en S4, S1 y S2; sus resultados se anexan cuando terminen.

## Baselines Naive, Naive+Trend y AR

Su division original es dinamica ("auto": prueba = max(720 h, 10 % de la serie)),
no una semana de 168 h. Los tres modulos ya aceptan enteros (`_resolver_split`),
asi que no hizo falta cambiar codigo: en las ventanas se ejecutan con
`train_hours=3600` (igual que la familia STL) y `forecast_horizon=168`. Sus
resultados **no son comparables con las corridas originales** (otra ventana), por
lo que la comparacion de S4 contra el original los marca `NO_COMPARABLE`.

## Otras limitaciones y hallazgos

1. **Cobertura de BCA**: en las copias locales BCA tiene historia completa
   (desde 2019); la excepcion de 384 h de `legacy_bca_reconstruido` correspondia a
   otro archivo. Confirmar en Drive.
2. **Desplazamiento de 1 h de Naive+T+S y AR sobre residuos**: los datos traen
   `Hora = 25` en el cambio de horario, de modo que la antigua condicion "toda la
   columna esta en [1,24]" fallaba y no se restaba 1 h a las etiquetas (commit
   `4512372`). Esos modelos parten train/test por posicion: solo cambiaron las
   etiquetas. La corrida de S4 lo comprobara.
3. **Procedencia de `tab:lstm_resultados`**: el repositorio declara que el script
   legacy se perdio; la unica implementacion reproducible es la LSTM univariada
   de `ensemble_stl.py` con `exog=None`. No se uso para S1-S4.
4. **Tolerancias de la reproduccion de S4** (propuestas): deterministicos
   (SARIMAX, Naive+T+S, AR resid) rtol 1e-6; arboles 1e-4; redes +-0.5 pp de MAPE
   por region.

## Plan de ejecucion por niveles

`vt.construir_configs(nivel, ventana)` / `vt.plan_dataframe()`. Las configuraciones
replican las de las Fases 1A/1B/2/3/4 de `run_matrix.ipynb`.

| Nivel | Contenido | Corridas por semana |
|---|---|---|
| T1 | sarimax, xgboost, lightgbm, naive_trend_seasonal, ar_resid_trend_seasonal, naive, naive_trend, ar | 8 |
| T2 | fcnn, lstm_resid, lstm_direct, ensemble_stl (5 exogenas) | 4 |
| T3 | individuales, Temperatura+IGAE y 7 combinaciones del trio de redes | 42 |

**Total: 54 por semana, 216 en las cuatro** (eran 51/204 antes de incluir los tres
baselines). El detalle esta en `docs/plan_corridas_ventanas.csv`.

Reparto de ejecucion (sin duplicados; columna `ejecuta_en` del plan): la **PC** corre
los modelos sin redes neuronales (naive, naive_trend, naive_trend_seasonal, ar,
ar_resid_trend_seasonal, sarimax, xgboost, lightgbm; 104 corridas) con
`scripts/run_local_estadisticos.py`; **Colab** corre las cuatro redes (fcnn,
lstm_resid, lstm_direct, ensemble_stl; 112 corridas). La PC es una i5-1035G1 de 4
nucleos / 8 hilos, 16 GB de RAM y sin GPU NVIDIA, por eso las redes van a Colab
(GPU). Ver `docs/INSTRUCCIONES_EJECUCION.md`.

## Salida consolidada

`vt.consolidar_ventanas(VENT_DIR, out_dir)` escribe en `.../Consolidado/`:

| Archivo | Contenido |
|---|---|
| `metricas_ventanas_largo.csv` | MAE, RMSE, MAPE, sMAPE por modelo x exogenas x estrategia x region x semana |
| `resumen_modelo_region_entre_semanas.csv` | media, desviacion estandar (ddof=1) y n por region |
| `resumen_modelo_semana.csv` | promedio entre regiones por semana |
| `resumen_modelo_global_entre_semanas.csv` | media y desviacion estandar entre semanas del promedio regional; indicador `completo_4_semanas_8_regiones` |
| `inventario_corridas_ventanas.csv` | regiones por corrida y semana |

Tiempos por corrida: `Pipeline_Resultados_Ventanas/_auditoria/tiempos_ventanas.csv`
(modelo, ventana, RUN_NAME, estado, duracion en segundos, error).
