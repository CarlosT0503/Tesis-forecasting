# Resume/checkpoint por region (2026-08-09)

## Causa del comportamiento anterior

Antes de este cambio, `run_experiment(config, ..., overwrite=True)` (usado
por `run_matrix()` para reintentar una config cuya carpeta existia pero
estaba incompleta) hacia:

```python
if reporte.es_completo:
    raise FileExistsError(...)   # nunca se toca una corrida completa

print("overwrite=True: se borra y se reintenta desde cero.")
shutil.rmtree(run_dir)           # <-- borra TODO, incluidas las regiones OK
os.makedirs(run_dir)
```

Es decir: la unica granularidad de "completo/incompleto" era la carpeta
ENTERA (8 regiones). Si 7 de 8 regiones habian terminado con exito y la
sesion de Colab se caia durante la region 8 (o fallaba con una excepcion),
`overwrite=True` borraba el resultado de las 7 regiones buenas junto con la
region 8 fallida, y las 8 volvian a correr desde cero. Para modelos con
Optuna + LSTM/FCNN esto significa horas de computo tirado por una sola
region problematica.

`_guardar_avance_csv()` (guardado incremental despues de cada region) ya
existia desde la migracion original y siempre escribio bien -- el problema
nunca fue que se perdiera lo ya guardado en disco, sino que **el mecanismo
de reintento no sabia leer lo que ya estaba guardado** antes de volver a
correr.

## Arquitectura nueva

### `src/tesis_forecast/checkpoint.py` (generico, sin saber nada de ningun modelo)

Dos funciones publicas:

- **`region_es_completa(nombre_serie, metricas_df, series_df, trials_df, config_usada_df, forecast_horizon=None, n_modelos_esperados=1, requiere_trials=False, requiere_config_usada=False, trials_esperados=None)`**
  Una region se considera completa solo si:
  1. Tiene exactamente `n_modelos_esperados` fila(s) de metricas (1 para la
     mayoria de los modelos; 2 para FCNN, que produce dos estrategias por
     region), todas con MAPE/sMAPE/MAE/RMSE finitos.
  2. Tiene predicciones: si `forecast_horizon` es un entero conocido,
     exactamente `forecast_horizon * n_modelos_esperados` filas de
     `tipo == "prediccion"`; si es `None` (split dinamico "auto" de
     Naive/Naive_Trend/AR, donde el conteo esperado depende del largo de
     la serie de esa region y no se puede saber sin recargar los datos
     crudos), basta con que haya al menos una.
  3. Si el modelo tunea (`requiere_trials=True`): al menos una fila de
     trials para esa serie (y, si se conoce un conteo exacto como el
     barrido de 168 lags de AR, exactamente esa cantidad -- detecta un
     barrido cortado a la mitad).
  4. Si el modelo registra hiperparametros (`requiere_config_usada=True`):
     exactamente `n_modelos_esperados` fila(s) de config_usada.

- **`cargar_checkpoint_regiones(output_dir, regions_all, ...)`**
  Lee `series.csv`/`metricas.csv`/`trials.csv`/`config_usada.csv` de
  `output_dir` (si existen; si falta o no se puede leer alguno, se trata
  como checkpoint vacio para ESE archivo, nunca como error), aplica
  `region_es_completa` a cada region de `regions_all`, y devuelve
  `(regiones_completas, previos)` -- el segundo elemento son los datos de
  esas regiones ya filtrados y listos para pre-sembrar el acumulador de
  resultados del modelo.

  `precargar_en_acumulador(resultados, previos)` hace esa siembra,
  defensiva ante modelos que no tienen `.trials`/`.config_usada` (Naive,
  Naive_Trend, Naive_Trend_Seasonal no tunean nada y no definen esos
  atributos).

### Dos formatos de "series" precargada

Los modelos migrados usan DOS convenciones distintas, ya existentes antes de
este cambio, para acumular `resultados.series`:

- **"filas"** (nativo de xgboost/lightgbm/lstm_direct/naive/naive_trend/ar,
  y tambien seguro para fcnn/naive_trend_seasonal/ar_resid_trend_seasonal/
  lstm_resid porque estos usan `_construir_df_series` con `np.atleast_1d`):
  una fila por registro, fecha/valor escalares. Es el formato que
  `cargar_checkpoint_regiones(..., formato_series="filas")` (el default)
  produce, leyendo directamente `series.csv` fila por fila.

- **"bloques"** (sarimax/ensemble_stl): un bloque por
  `(serie, tipo, subset, modelo)` con fecha/valor como arreglo. Estos dos
  modulos construyen su DataFrame de series con
  `pd.DataFrame({...bloque...})` **sin** ninguna normalizacion tipo
  `np.atleast_1d` -- pasarles filas escalares sueltas reproduciria
  exactamente el bug que tuvo FCNN
  (`ValueError: If using all scalar values, you must pass an index`, ver
  `docs/MODELOS_MIGRADOS.md`). `cargar_checkpoint_regiones(...,
  formato_series="bloques")` agrupa las filas leidas de `series.csv` de
  vuelta en bloques con `fecha`/`valor` como arreglo antes de
  devolverlas, para que encajen sin tocar la logica de guardado de esos
  dos modulos.

Se eligio esta dualidad (en vez de forzar un unico formato universal) por
ser la opcion mas conservadora: preserva el codigo de guardado de cada
modelo exactamente como estaba, en vez de reescribirlo para unificarlo --
lo segundo si hubiera sido un cambio de arquitectura, no una adicion.

### Integracion en cada `run()` (12 modelos)

El mismo bloque, con parametros ajustados por modelo, se agrego justo
despues de `resultados = _ResultsAccumulator()` y antes de
`regiones = cargar_regiones(regions_all, data_dir)` (que pasa a recibir
`regiones_pendientes` en vez de `regions_all`):

```python
regiones_completas, previos = cargar_checkpoint_regiones(
    output_dir, regions_all, forecast_horizon=forecast_horizon,
    requiere_trials=..., requiere_config_usada=..., ...
)
precargar_en_acumulador(resultados, previos)

regiones_pendientes = [r for r in regions_all if r not in regiones_completas]
...
regiones = cargar_regiones(regiones_pendientes, data_dir)
```

Ningun otro cambio: el loop `for region, df in regiones.items(): ...`, el
guardado incremental (`_guardar_avance_csv`) y la agregacion final son
exactamente los de antes -- ya incluian por diseno cualquier dato que
estuviera en `resultados.*`, sin importar si vino de una region recien
calculada o precargada del checkpoint.

| Modelo | Familia series | n_modelos | trials | config_usada |
|---|---|---|---|---|
| xgboost | filas | 1 | Optuna (variable) | si |
| lightgbm | filas | 1 | Optuna (variable) | si |
| lstm_direct | filas | 1 | Optuna (variable) | si |
| naive | filas | 1 | no | no |
| naive_trend | filas | 1 | no | no |
| ar | filas | 1 | 168 exactas (barrido AIC) | si |
| fcnn | bloques (atleast_1d) | **2** | Optuna x2 (variable) | si (x2) |
| naive_trend_seasonal | bloques (atleast_1d) | 1 | no | no |
| ar_resid_trend_seasonal | bloques (atleast_1d) | 1 | 168 exactas | si |
| lstm_resid | bloques (atleast_1d) | 1 | Optuna (variable) | si |
| sarimax | bloques (sin guarda) | 1 | no | si |
| ensemble_stl | bloques (sin guarda) | 1 | Optuna x2 + 168 AR (variable) | si |

### `runner.py`: `overwrite=True` deja de borrar la carpeta

```python
# antes:
shutil.rmtree(run_dir)
os.makedirs(run_dir)

# ahora:
os.makedirs(run_dir, exist_ok=True)   # la carpeta se conserva tal cual
```

`config.json` se reescribe igual que antes (contenido deterministico a
partir de la config, no cambia nada). `log.txt` sigue en modo `"a"`
(append), asi que el historial de corridas anteriores sobre esa carpeta se
conserva. Quien decide que region recalcular ya no es `runner.py` sino cada
`MODEL_RUNNERS[modelo]`, via el checkpoint descrito arriba.

`matrix.py` no necesito ningun cambio de logica -- ya llamaba
`run_experiment(config, ..., overwrite=True)` cuando `validar_resultado()`
decia incompleto; ese mismo llamado ahora reanuda en vez de reiniciar,
automaticamente.

### Una corrida completa sigue siendo inmutable

Sin cambios: `run_experiment()` sigue llamando `validar_resultado(run_dir)`
antes de tocar una carpeta existente, y si `es_completo` es `True`, sigue
lanzando `FileExistsError` incluso con `overwrite=True`. El checkpoint por
region solo actua sobre carpetas que `validar_resultado()` ya considero
incompletas.

## Region parcial o corrupta

No hace falta ninguna logica especial de "borrado selectivo": una region
que no cumple TODOS los criterios de `region_es_completa` simplemente no
entra en `regiones_completas`, y por lo tanto sus filas (si las tenia,
parciales) **no se copian** a `previos` ni se pre-siembran en
`resultados`. Esa region se vuelve a calcular desde cero como si nunca
hubiera corrido. Cuando `_guardar_avance_csv`/la agregacion final
sobreescriben `series.csv`/`metricas.csv`/etc. (con `to_csv(...)`, no en
modo append), las filas viejas y parciales de esa region quedan
reemplazadas por las nuevas -- las regiones sanas, mientras tanto, se
preservan intactas porque sus filas si se precargaron.

## Tests (`tests/test_checkpoint.py`)

Sin `pytest` (mismo estilo que el resto de `tests/`, scripts ejecutables
directamente). Dos partes:

1. **Unitarios de `checkpoint.py`** con CSV sinteticos escritos a mano
   (rapidos, sin entrenar ningun modelo): criterios de
   `region_es_completa` (metricas NaN, conteo de predicciones, trials/
   config_usada faltantes o incompletos, `n_modelos_esperados=2`),
   `cargar_checkpoint_regiones` en formato "filas" y "bloques", region
   parcial excluida, 8/8 completas, y que precargar + agregar una region
   nueva no duplica filas.

2. **End-to-end reales** contra `naive_trend_seasonal_model.py` (Family B,
   rapido: STL sin LSTM/Optuna/AR) y `ar_model.py` (Family A, CON
   trials/config_usada, 2 regiones) cubriendo los 5 escenarios pedidos:
   - run nuevo (3/8 regiones con datos disponibles);
   - aparecen las 5 restantes, se reanuda con las 8: las 3 originales NO
     se recalculan (mismo MAPE exacto, comparado numero por numero);
   - 8/8 completas: correr de nuevo es un skip total (mismo MAPE en las
     8, cero trabajo nuevo);
   - se corrompe `series.csv` de una region (se le borran manualmente 50
     de sus 168 filas de prediccion) y se vuelve a correr: esa region se
     re-ejecuta COMPLETA (168 predicciones de nuevo), las otras 7 no se
     tocan;
   - en cada paso se verifica el conteo total de filas de
     `series.csv`/`metricas.csv`/`trials.csv` para confirmar que nunca
     hay una serie duplicada.

Ver el reporte de la conversacion para los resultados exactos de esta
corrida.
