# Compatibilidad con automatizacion futura (cola/matriz nocturna)

**Actualizado 2026-08-08**: `matrix.py` y `validator.py` ya existen (ver
puntos 2, 5 y 7 abajo, actualizados) — este documento originalmente audito
solo `run_experiment()` bajo el supuesto de que la cola/matriz vendria
despues; ahora la cola minima (`run_matrix()`) ya esta implementada. Sigue
sin existir scheduling por hora ni infraestructura de nube (punto 4 de
"que falta").

Ningun cambio de este documento ni de `matrix.py`/`validator.py` toco la
logica de modelado de ningun modelo (arquitectura, hiperparametros, Optuna,
tratamiento de exogenas, metricas).

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

**Implementado.** `resolve_run(config)` y `experiment_exists(config)`
siguen existiendo como antes, y `run_matrix()` (en `matrix.py`) ya los usa
en la practica: por cada config, si `run_dir` existe y `validar_resultado()`
lo confirma completo, se salta; si existe pero esta incompleto, se
reintenta con `overwrite=True` (ver punto 5 y el flag `overwrite` en
`run_experiment()`).

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

**Implementado.** `validator.py::validar_resultado(run_dir)` lee solo
archivos (config.json/metricas.csv), no ejecuta nada, y devuelve un
`ValidationReport` con `es_completo`, `problemas` (lista legible),
`regiones_encontradas`/`regiones_faltantes` y conteo de filas con NaN en
MAPE/sMAPE/MAE/RMSE. Nota: como `metricas.csv` puede tener mas de una fila
por region (FCNN tiene 2: directa y STL-residuos), la validacion compara
por `region` unica, no por numero total de filas.

Se usa en dos lugares: dentro de `run_experiment(..., overwrite=True)`
antes de decidir si borra una carpeta existente (nunca borra una completa),
y dentro de `run_matrix()` para decidir saltar vs. reintentar cada config.

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

**Implementado.** `run_matrix()` acumula un `MatrixRunRecord` por config
(status `completed`/`skipped_ya_completo`/`failed`, `mape_promedio`,
`error`, `run_dir`) y al final imprime el resumen (totales, MAPE por
corrida completada, lista de fallidas con su error). `resumen_dataframe()`
convierte esa lista en un DataFrame para inspeccionar en el notebook.

Para cada corrida individual, `run_experiment()` devuelve un
`ExperimentResult` en vez de solo la ruta:

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

## Que falta para la automatizacion nocturna completa

Con `matrix.py` y `validator.py` ya implementados, lo que queda es:

1. Aislar fallos por region dentro de un mismo experimento (gap
   mencionado en el punto 3), si se decide que vale la pena para correr
   overnight sin supervision.
2. Expandir `run_matrix()` para aceptar una matriz/YAML declarativo
   (producto cartesiano de modelos x exogenas x train_hours) en vez de una
   lista de `ExperimentConfig` ya armada a mano -- hoy `run_matrix()` ya
   acepta cualquier lista, solo falta el generador de esa lista.
3. Un mecanismo de disparo (cron, notebook programado, Colab Pro
   scheduled runtime, o Vertex/Cloud Run si se decide salir de Colab) —
   esto es la "infraestructura de nube" explicitamente fuera de alcance
   por ahora.
