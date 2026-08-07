# Compatibilidad con automatizacion futura (cola/matriz nocturna)

Este documento audita `run_experiment()` (y `run_experiment()` solamente —
no se construyo scheduler, matrix runner ni infraestructura de nube) contra
los 8 requisitos futuros pedidos, y deja constancia de que se hizo en cada
caso: ya estaba resuelto, se agrego una pieza minima y no invasiva, o se
deja explicitamente pendiente para un modulo futuro.

Ningun cambio de este documento toco la logica de modelado de
`xgboost_model.py` (arquitectura, hiperparametros, Optuna, tratamiento de
exogenas, metricas). Los cambios fueron todos en `runner.py`.

## 1. Ejecutar experimentos secuencialmente

**Ya compatible, sin cambios.** `run_experiment()` no depende de estado
global mutable entre llamadas (los acumuladores de resultados ya vivian
dentro de cada llamada desde la extraccion de XGBoost). Un futuro
`matrix.py` puede hacer simplemente:

```python
for config in configs:
    run_experiment(config)
```

## 2. Detectar cuales ya existen y saltarlos

**Se agrego `resolve_run(config)` y `experiment_exists(config)`.**

Antes, el calculo de RUN_NAME/ruta de salida vivia mezclado dentro de
`run_experiment()`. Ahora es una funcion pura y reutilizable
(`resolve_run`), y `experiment_exists()` la usa para responder
"esta config ya se corrio" sin ejecutar nada. Un futuro matrix runner:

```python
for config in configs:
    if experiment_exists(config):
        continue
    run_experiment(config)
```

Limitacion documentada en el docstring de `experiment_exists()`: requiere
que Drive ya este montado, si no siempre devuelve `False` (falso negativo,
no una confirmacion).

## 3. Continuar con el siguiente si uno falla

**Ya compatible, sin cambios de comportamiento.** `run_experiment()` sigue
levantando excepciones (`FileExistsError`, `ValueError`, o cualquier error
no capturado del pipeline) en vez de tragárselas. El contrato para un
futuro loop es el estandar de Python:

```python
for config in configs:
    try:
        resultado = run_experiment(config)
    except Exception as e:
        registrar_fallo(config, e)
        continue
```

Importante para calibrar expectativas: dentro de una misma corrida, los
errores **por region** (por ejemplo un archivo `_GEN.csv` faltante durante
`merge_exogenas`, fuera del `try/except` de `evaluar_serie`) siguen
propagandose y abortan el resto de las regiones de ESE experimento — este
es el mismo comportamiento que tenia la celda 49 original y no se cambio
(cambiarlo ahora habria alterado el pipeline que se esta validando contra
el legacy). Aislar fallos por region dentro de un mismo experimento es un
gap real, pero deliberadamente no tocado en esta pasada.

## 4. Guardar logs y errores por experimento

**Se agrego `log.txt` dentro de la carpeta del run.** Es un archivo nuevo,
fuera de la lista de 5 archivos ya acordada (`config.json`, `series.csv`,
`metricas.csv`, `trials.csv`, `config_usada.csv`) mas el ya existente
`optuna_xgboost.db`. `run_experiment()` duplica (tee) todo lo que el
pipeline imprime hacia ese archivo ademas de la salida normal de la celda
de Colab, sin agregar ni modificar ningun `print()` dentro de
`xgboost_model.py`. Si la corrida falla, el traceback completo se agrega al
mismo `log.txt` antes de relanzar la excepcion.

Estructura final de una carpeta de experimento:

```
Pipeline_Resultados/<RUN_NAME>/
├── config.json
├── series.csv
├── metricas.csv
├── trials.csv
├── config_usada.csv
├── optuna_xgboost.db   (mecanismo de storage de Optuna, no un entregable)
└── log.txt             (nuevo: stdout completo + traceback si fallo)
```

## 5. Validar automaticamente resultados completos (8 regiones, sin NaN, etc.)

**No implementado a proposito.** No se construyo un validador. Lo que si
se aseguro es que la validacion se pueda escribir despues como una funcion
que solo LEE archivos, sin tocar `run_experiment()`:

- `metricas.csv` tiene una fila por region con columnas numericas
  (`MAPE`, `sMAPE`, `MAE`, `RMSE`) — un futuro `validar(run_dir)` puede
  chequear `len(df) == 8` y `df[...].isna().any()` directamente.
- `ExperimentResult` (ver mas abajo) ya trae `regiones_esperadas` y
  `regiones_con_metricas` calculados al momento de terminar la corrida, sin
  necesidad de releer el CSV, como primera señal rapida de completitud.

## 6. Conservar resultados parciales si una ejecucion se interrumpe

**Ya compatible desde la extraccion original, sin cambios.**
`_guardar_avance_csv()` escribe `series.csv` / `metricas.csv` /
`trials.csv` / `config_usada.csv` en disco despues de CADA region, no solo
al final. Si Colab se desconecta a medio pipeline, lo ya guardado
sobrevive; solo se pierde el trabajo de la region que estaba en progreso en
ese momento. `log.txt` (punto 4) tambien queda escrito hasta el punto de la
interrupcion porque se usa modo `"a"` (append) y se hace flush en cada
escritura via el tee.

## 7. Resumen final de corridas completadas/fallidas y sus metricas

**No implementado a proposito** (es, literalmente, el matrix runner). Lo
que se agrego es la pieza que ese resumen va a necesitar por cada corrida:
`run_experiment()` ahora devuelve un `ExperimentResult` en vez de solo la
ruta:

```python
@dataclass
class ExperimentResult:
    run_name: str
    run_dir: str
    status: str  # "completed" -- run_experiment() nunca devuelve "failed",
                 # levanta una excepcion; un futuro loop construye su propio
                 # registro con status="failed" a partir del except, con
                 # los mismos nombres de campo para poder unir ambos casos
                 # en una sola tabla resumen.
    regiones_esperadas: int
    regiones_con_metricas: int
    mape_promedio: float | None
    archivos: dict  # nombre logico -> ruta (config, series, metricas, ...)
```

Un futuro `matrix.py` simplemente acumula estos objetos (mas los
"failed" que construya el propio loop) en una lista o DataFrame.

## 8. Que un agente (Claude u otro) inspeccione despues logs/resultados

Servido por los puntos 4 y 7: cada carpeta de experimento es autocontenida
y legible sin ejecutar nada — `config.json` dice exactamente que se
configuro, `log.txt` dice que paso paso a paso (incluyendo el traceback si
fallo), y los CSV son tabulares y con columnas documentadas (ver
`docs/DATOS_REQUERIDOS.md` para los datos de entrada; los formatos de
salida estan documentados como comentarios en `xgboost_model.py` y en el
checklist de equivalencia entregado con la migracion de XGBoost).

## Que falta para la automatizacion nocturna completa (fuera de esta pasada)

Con las piezas de arriba, lo que realmente falta construir despues es
poco y esta bien acotado:

1. `matrix.py`: expandir una lista/YAML de configs, hacer el loop
   `experiment_exists -> run_experiment -> try/except`, acumular
   `ExperimentResult`.
2. `validator.py`: leer `metricas.csv`/`series.csv` de un `run_dir` y
   devolver un veredicto de completitud (regiones, NaNs, longitud del
   horizonte).
3. Aislar fallos por region dentro de un mismo experimento (gap
   mencionado en el punto 3), si se decide que vale la pena para correr
   overnight sin supervision.
4. Un mecanismo de disparo (cron, notebook programado, Colab Pro
   scheduled runtime, o Vertex/Cloud Run si se decide salir de Colab) —
   esto es la "infraestructura de nube" explicitamente fuera de alcance
   por ahora.
