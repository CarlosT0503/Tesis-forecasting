# Instrucciones de ejecucion (216 corridas, 4 semanas)

## Reparto (no duplicar)

| Donde | Modelos | Corridas |
|---|---|---|
| **PC** (`scripts/run_local_estadisticos.py`) | naive, naive_trend, naive_trend_seasonal, ar, ar_resid_trend_seasonal, sarimax, **xgboost, lightgbm** (T1 y T3) | 104 (26 por semana) |
| **Colab** (`notebooks/run_ventanas.ipynb`) | fcnn, lstm_resid, lstm_direct, ensemble_stl (T2 y T3) | 112 (28 por semana) |

La columna `ejecuta_en` de `docs/plan_corridas_ventanas.csv` lo dice para cada corrida.
El cuaderno solo lanza lo marcado `colab`; el script local solo lo marcado `local`.

## Colab (lanzar y dejar)

1. Colab -> *Archivo -> Abrir cuaderno -> GitHub* -> `CarlosT0503/Tesis-forecasting`, rama `main`, `notebooks/run_ventanas.ipynb`.
2. Entorno de ejecucion -> **GPU (T4)**.
3. Celda de codigo **1** (Setup; autorizar Drive). Debe imprimir la version del repositorio y no fallar los `assert`.
4. Celda **2** (Auditoria) y **3** (Estado): solo lectura, opcionales.
5. Celda **4** (Lanzamiento) con `SESION = "A"` y dejarla. Segunda pestana opcional: `SESION = "B"`. Nunca la misma sesion en dos pestanas.

**Si se corta:** volver a ejecutar las celdas 1 y 4. Lo completo se salta; lo parcial continua desde la ultima region guardada.

## PC

Un unico **supervisor** (`scripts/cola_local.py`, entorno `.venv_local`) corre en segundo plano y no depende de ninguna sesion de chat:

```powershell
powershell -Command "Start-Process .venv_local\Scripts\python.exe -ArgumentList 'scripts\cola_local.py' -WindowStyle Hidden"
```

- Prioridad: XGBoost/LightGBM T1 -> SARIMAX T1 -> XGBoost/LightGBM T3 -> SARIMAX T3 (este ultimo arranca solo cuando no queda nada mas prioritario).
- Maximo 3 procesos a la vez (2 SARIMAX como mucho mientras queden arboles), 1 hilo BLAS/OpenMP por proceso, escalonados 20 s.
- No lanza trabajos nuevos con menos de 1.2 GB de RAM libre ni con bateria < 30 % sin corriente; deja de mantener la PC despierta si salta una proteccion. No cambia ajustes de energia.
- Reanuda desde los checkpoints: relanzar el supervisor no repite nada completo. Un fallo se reintenta 2 veces.
- Estado en vivo: `resultados_locales/cola/estado_cola.json` y `supervisor.log`; un log por trabajo en esa carpeta.

## Copiar resultados de la PC a Drive

Cuando terminen, copiar el *contenido* de `resultados_locales/Pipeline_Resultados_Ventanas/` (carpetas `S1`..`S4` y `_auditoria`) dentro de `MyDrive/Pipeline_Resultados_Ventanas/`. No hay conflictos: PC y Colab escriben corridas distintas y archivos de tiempos con nombres distintos (`tiempos_local_*.csv`, `tiempos_colab_<sesion>.csv`).

## Garantias

- Resultados originales (`Pipeline_Resultados/`): solo lectura.
- Una corrida completa nunca se sobrescribe; una incompleta se reanuda en su misma carpeta.
- Cada corrida tiene su propio estudio Optuna dentro de su carpeta (separados por semana).
- Naive, Naive_Trend y AR (3600 h de entrenamiento) son una **configuracion nueva** de la extension; no se mezclan con los resultados historicos.
