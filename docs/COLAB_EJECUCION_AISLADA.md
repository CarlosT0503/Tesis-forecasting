# Colab: ejecución aislada, telemetría y reanudación (2026-10-20)

Cambios para que las 112 corridas neuronales terminen aunque falle la memoria. **No cambian hiperparámetros, ventanas, datos ni métricas**, y no tocan resultados ya obtenidos.

## Qué se cambió

| # | Cambio | Dónde |
|---|---|---|
| A | **Telemetría** de RAM (sistema y procesos) y GPU cada 2 min, con registro persistente en Drive | `src/tesis_forecast/telemetria.py` |
| B | **Un subproceso por configuración**: al terminar, el sistema operativo recupera toda la memoria. Si un subproceso muere, se registra, se clasifica y la cola sigue | `src/tesis_forecast/colab_aislado.py`, `scripts/run_config_aislada.py` |
| C | **Escritura atómica** de los CSV (temporal en la misma carpeta y reemplazo) en las cuatro redes y en el runner | `src/tesis_forecast/atomic_io.py` |
| D | **LSTM directa**: al reanudar solo corre los intentos de Optuna que faltan para llegar a 10 | `models/lstm_direct.py` (`_intentos_pendientes`) |
| — | Notebook: celda 3 (progreso), celda 4 (lanzamiento con `SESION`, `LOTE`, `MAX_INTENTOS`) y celda 1 (verifica el código nuevo) | `notebooks/run_ventanas.ipynb` |

## Cómo funciona una corrida

1. La celda 4 construye la cola de la sesión (A = S4 y S1; B = S2 y S3), en el orden de siempre (T2 antes que T3), opcionalmente filtrada por `LOTE`.
2. Para cada configuración: si la carpeta ya está completa (8 regiones, sin NaN) **no se lanza nada**. Si no, se lanza `scripts/run_config_aislada.py`, que ejecuta el mismo `run_matrix([config])` de siempre: salta las regiones completas y retoma las parciales desde el checkpoint.
3. El proceso padre vigila al hijo (RAM libre mínima y pico de RSS) y, al terminar, **clasifica** el resultado.
4. Reintentos acotados: hasta `MAX_INTENTOS` (3) por configuración y **se abandona si 2 intentos seguidos no agregan ninguna región**. Si **3 configuraciones seguidas** fallan por RAM, la cola se detiene (el entorno no alcanza).
5. Al detener la celda (Interrumpir ejecución), el padre termina el árbol de procesos del hijo para que no quede ocupando RAM/GPU.

## Clases de fallo (`subprocesos_colab_<A|B>.csv`, columna `clase`)

| Clase | Qué significa | ¿Cuenta como RAM? |
|---|---|---|
| `ram_sistema` | El subproceso murió por SIGKILL con la RAM del sistema agotada (OOM-killer). No deja traceback | **Sí** |
| `ram_python` | `MemoryError` / `std::bad_alloc` (hay traceback) | **Sí** |
| `gpu_memoria` | `ResourceExhaustedError` / "OOM when allocating tensor" / CUDA OOM. **Memoria de GPU, no de RAM** | No |
| `sigkill_otro` | SIGKILL con RAM holgada (algo externo lo mató) | No |
| `interrumpido` | SIGTERM / SIGINT | No |
| `fallo_nativo` | SIGSEGV / SIGABRT en una librería nativa | No |
| `timeout` | Superó `timeout_s` (por defecto sin límite) | No |
| `incompleta` | Terminó sin error pero la corrida no tiene las 8 regiones | No |
| `error_codigo` | Excepción de Python distinta de memoria | No |

Nota: un SIGKILL sin dato de RAM se clasifica como `ram_sistema` (lo más probable en Colab). La **GPU** se trata aparte: TensorFlow reserva casi toda la GPU en el primer uso, así que verla llena en `nvidia-smi` no es una fuga; el subproceso se lanza con `TF_FORCE_GPU_ALLOW_GROWTH=true` (solo cambia *cómo* se reserva la memoria de GPU, no los cálculos), de modo que `gpu_usada_mb` refleje el uso real.

## Archivos que se generan (`Pipeline_Resultados_Ventanas/_auditoria/`)

| Archivo | Contenido |
|---|---|
| `telemetria_colab_<A\|B>.csv` | Cada 2 min: RAM total/disponible/usada %, RSS del cuaderno y de sus subprocesos, GPU usada/total/utilización y la corrida en curso. Si Drive no está escribible, se guarda en `/tmp` |
| `subprocesos_colab_<A\|B>.csv` | Una fila por intento: corrida, código de salida, clase, duración, regiones antes/después, pico de RSS, RAM mínima libre y último mensaje |
| `tiempos_colab_<A\|B>.csv` | Una fila por configuración (como antes) |
| `faltan_colab.csv` | Lo que falta, escrito por la celda 3 |

## Reanudación (sin repetir regiones completas)

- Cada región se guarda al terminar (4 CSV, ahora de forma atómica: temporal `.tmp_*.part` en la misma carpeta y `os.replace`). Una caída durante el guardado deja intactos los CSV anteriores; el temporal huérfano se borra al relanzar.
- Al reanudar se salta toda región con métricas finitas, 168 predicciones, intentos de Optuna y configuración (`checkpoint.py`). La LSTM directa ahora también respeta el presupuesto de Optuna dentro de una región cortada a mitad.
- **Aviso sobre corridas anteriores de la LSTM directa:** antes de este cambio, una región reanudada a mitad podía acumular más de 10 intentos. La celda 3 lista las regiones cuyo `trials.csv` tenga un número de intentos distinto de 10; esas regiones usaron un presupuesto mayor al del diseño y conviene declararlo o repetirlas.

## Pruebas (`tests/`)

| Archivo | Qué prueba |
|---|---|
| `test_atomic_io.py` | Escritura atómica: bytes idénticos a `to_csv`, fallos sin corromper, temporal en la misma carpeta, guardado de las 4 redes |
| `test_lstm_direct_resume.py` | Optuna real: 10 → 0 intentos nuevos al reanudar; 3 hechos → corre 7; intento cortado o RUNNING no cuenta |
| `test_telemetria.py` | Muestras de RAM/GPU, respaldo sin psutil, registro persistente fila a fila, ruta de Drive |
| `test_ejecucion_aislada.py` | Clasificación; cola y lotes (A y B = 112, lotes particionan 56); subprocesos simulados (éxito, reintento con avance, abandono, cada clase, timeout sin huérfanos, corte por RAM); **ejecución real de extremo a extremo** con el modelo naive: corrida completa → truncada a 3 regiones → reanudada sin recalcular las 3 y con resultado idéntico |
| `test_notebook_ventanas.py` | El notebook coincide con sus celdas, las celdas 3 y 4 se ejecutan (sesiones A y B) |

Limitación: las redes neuronales no se pudieron ejecutar localmente (la PC no tiene TensorFlow ni GPU); lo que se probó son la lógica de guardado, reanudación, aislamiento y clasificación, no el entrenamiento en sí. La primera ejecución en Colab es, por tanto, la prueba final: conviene empezar con `LOTE = "T2"`.

## Actualización 2026-10-21: errores por región visibles y corridas sin resultados = fallidas

**Problema detectado en Colab (Ensemble STL, S4 y S1, T2):** rc=0 y 0/8 regiones. Causa del *síntoma*: los modelos neuronales envuelven cada región en un `try/except Exception` que solo imprimía una línea y seguía; si todas fallaban, `run()` devolvía tablas vacías, `run_experiment` escribía CSV vacíos y registraba la corrida como `completed`. La excepción concreta se identifica con la traza (ver abajo); el cálculo no se ha tocado.

Cambios (no alteran cálculos, hiperparámetros ni resultados existentes):

| Cambio | Dónde |
|---|---|
| Cada error tragado imprime una marca `@@ERROR_REGION@@ <región> \| <Tipo> \| <mensaje>`, la **traza completa** y `@@FIN_ERROR@@` (stdout, que el runner copia a `log.txt`). Los mensajes anteriores se conservan | `errores_log.py`; `ensemble_stl.py`, `fcnn_model.py` (3 puntos), `lstm_direct.py`, `lstm_resid_model.py` |
| Si **ninguna** región produjo métricas (ni nuevas ni heredadas del checkpoint) la corrida **falla** (`RuntimeError` con el primer error real); los CSV quedan guardados | `runner.py` |
| El subproceso termina con **código 3** si acabó sin excepción pero la corrida no tiene las 8 regiones, y su JSON trae `errores_region` y `regiones_ok` | `scripts/run_config_aislada.py` |
| El orquestador usa esos errores: el mensaje de `subprocesos_colab_<A\|B>.csv` cita la excepción real; un `ResourceExhaustedError` o `MemoryError` tragado por el modelo se clasifica como `gpu_memoria` / `ram_python` (no como `incompleta`); si todas las regiones fallan con **el mismo error** y sin avanzar, se abandona tras **1** intento (fallo determinista) | `colab_aislado.py` |

Sin cambios de esquema: el CSV de intentos conserva sus columnas (el detalle va en `mensaje`).

**Dónde ver el error de una corrida:** `Pipeline_Resultados_Ventanas/<S#>/<RUN_NAME>/log.txt` → `!grep -n -A25 "@@ERROR_REGION@@" "<ruta>/log.txt" | head -80`. Las ejecuciones se identifican por la línea `Experimento: <RUN_NAME>`; el orquestador solo cuenta los errores de la ejecución actual.

Pruebas: `tests/test_errores_log.py` (marca y traza, los 4 modelos, runner fallido/completado, rc=3, GPU/RAM tragados, abandono determinista, falla real del subproceso) y regresión de `test_ejecucion_aislada.py` (reanudación real con el modelo naive), `test_checkpoint.py`, `test_notebook_ventanas.py`, etc.

## Actualización 2026-10-22: causa raíz de Ensemble STL (statsmodels 0.15.0) y corrección

**Causa (confirmada en Colab):** Colab pasó a **statsmodels 0.15.0**, cuyo `AutoReg` ya no acepta el argumento `old_names` (`TypeError: AutoReg.__init__() got an unexpected keyword argument 'old_names'`). `seleccionar_ar_por_aic` llamaba a `AutoReg(..., old_names=False)` y atrapaba la excepción de **cada uno de los 168 candidatos**, de modo que ninguno resultaba válido y cada región terminaba con `RuntimeError: No se pudo ajustar ningun AR valido.`, siempre después de entrenar y predecir con la LSTM y la FCNN. Sin ese argumento el ajuste funciona (en Colab, AIC = 10212.775 con una serie sintética; reproducido localmente con la versión 0.15.0 real: mismo valor).

**Corrección mínima (`ensemble_stl.py`):**
1. Se elimina `old_names=False` de la llamada. En statsmodels 0.13 a 0.14 su valor por defecto ya es `False`, así que el ajuste es el mismo.
2. Si todos los candidatos fallan, el `RuntimeError` conserva su texto y añade la causa: longitud del residuo, excepciones con su tipo y conteo (p. ej. `TypeError: ... 'old_names' x168`) y candidatos con AIC no finito. La selección no cambia.

**Equivalencia verificada (datos reales de S4, función corregida):** CEN, NES y PEN con statsmodels 0.14.5 y 0.15.0 reales dan resultados **idénticos bit a bit** en STL (tendencia, estacionalidad, residuo), rezago elegido (168), AIC de los 168 candidatos, parámetros y predicción a 168 h. También idénticos al código anterior (con `old_names=False`) en 0.14.5. Prueba: `tests/test_ensemble_ar_compat.py` (el punto 5 usa `SM015_PATH`, una carpeta con statsmodels 0.15.0 instalada aparte con `pip install --no-deps --target`).

**Reutilización de lo ya hecho (sin repetir la optimización neuronal):** las 16 bases Optuna de cada corrida (`<REGION>_DEMANDA_LSTM_trend_EXOG_ALL_optuna.db` y `..._FCNN_seasonal_EXOG_ALL_optuna.db`) traen 5 intentos completos; al reanudar el módulo lee "completos: 5, restantes: 0" y devuelve parámetros y `trials` desde la base sin entrenar ni agregar intentos. Los CSV vacíos (5 bytes) que dejó la corrida fallida se tratan como ausentes (checkpoint y `validar_resultado`; verificado). Sí se repite, por región, el **entrenamiento final** de la LSTM y de la FCNN. Los pesos finales pueden diferir ligeramente de una corrida ininterrumpida porque, al saltarse la optimización, cambia el estado del generador aleatorio; es la limitación habitual de toda reanudación y conviene declararla.

**Otros usos de `old_names=False` (documentados, NO modificados):**

| Archivo | Línea | Dónde corre | Efecto con statsmodels ≥ 0.15 |
|---|---|---|---|
| `models/ar_model.py` | 76 | PC (modelo `ar`) | Fallaría igual que Ensemble STL |
| `models/ar_resid_trend_seasonal_model.py` | 168 | PC (modelo `ar_resid_trend_seasonal`) | Fallaría igual |

Hoy no hay problema: la PC usa statsmodels 0.14.5 y esas 8 corridas locales (T1) ya están completas. Mientras corre la cola local no se tocan estos modelos. Si alguien actualiza statsmodels en la PC, hay que aplicar la misma corrección (quitar el argumento; equivalencia ya verificada en 0.14.5). `sarimax_model.py` no usa `AutoReg`.
