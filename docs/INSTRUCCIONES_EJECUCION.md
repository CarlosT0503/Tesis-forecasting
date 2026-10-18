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

Procesos en segundo plano (no hace falta lanzarlos de nuevo salvo que se apague la PC):

| Proceso | Que hace | Reanudar si se interrumpe |
|---|---|---|
| SARIMAX T1 (uno por semana) | `scripts/run_local_estadisticos.py --ventanas <S#> --modelos sarimax` | mismo comando |
| SARIMAX T3 (cadenas por semana) | arrancan solos al terminar T1 de su semana | `python scripts/run_local_estadisticos.py --ventanas S4 S1 S2 S3 --niveles T3 --modelos sarimax` |
| XGBoost y LightGBM (T1 y luego T3) | `powershell -File scripts\lanzar_arboles_local.ps1` (usa el entorno aislado `.venv_local`) | mismo comando |

Los scripts nuevos limitan BLAS/OpenMP a **un hilo por proceso** para que varios procesos no se estorben. `.venv_local/` es un entorno aislado (pandas 2.2.3, numpy 2.2.3, statsmodels 0.14.5, scikit-learn 1.6.1, optuna 5.0.0, xgboost 3.4.1, lightgbm 4.7.0): no toca el Python principal.

## Copiar resultados de la PC a Drive

Cuando terminen, copiar el *contenido* de `resultados_locales/Pipeline_Resultados_Ventanas/` (carpetas `S1`..`S4` y `_auditoria`) dentro de `MyDrive/Pipeline_Resultados_Ventanas/`. No hay conflictos: PC y Colab escriben corridas distintas y archivos de tiempos con nombres distintos (`tiempos_local_*.csv`, `tiempos_colab_<sesion>.csv`).

## Garantias

- Resultados originales (`Pipeline_Resultados/`): solo lectura.
- Una corrida completa nunca se sobrescribe; una incompleta se reanuda en su misma carpeta.
- Cada corrida tiene su propio estudio Optuna dentro de su carpeta (separados por semana).
- Naive, Naive_Trend y AR (3600 h de entrenamiento) son una **configuracion nueva** de la extension; no se mezclan con los resultados historicos.
