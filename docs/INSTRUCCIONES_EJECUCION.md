# Instrucciones de ejecucion (216 corridas, 4 semanas)

## Reparto (no duplicar)

| Donde | Modelos | Corridas |
|---|---|---|
| **PC** (`scripts/run_local_estadisticos.py`) | naive, naive_trend, naive_trend_seasonal, ar, ar_resid_trend_seasonal, sarimax, **xgboost, lightgbm** (T1 y T3) | 104 (26 por semana) |
| **Colab** (`notebooks/run_ventanas.ipynb`) | fcnn, lstm_resid, lstm_direct, ensemble_stl (T2 y T3) | 112 (28 por semana) |

La columna `ejecuta_en` de `docs/plan_corridas_ventanas.csv` lo dice para cada corrida.
El cuaderno solo lanza lo marcado `colab`; el script local solo lo marcado `local`.

## Colab (lanzar y dejar)

Detalle del mecanismo (un subproceso por configuración, telemetría, clases de fallo): `docs/COLAB_EJECUCION_AISLADA.md`.

1. Colab -> *Archivo -> Abrir cuaderno -> GitHub* -> `CarlosT0503/Tesis-forecasting`, rama `main`, `notebooks/run_ventanas.ipynb`.
2. Entorno de ejecucion -> **GPU (T4)**.
3. Celda de codigo **1** (Setup; autorizar Drive). Debe imprimir la version del repositorio, la memoria inicial y no fallar los `assert`. Si el `assert` dice "Codigo desactualizado": *Entorno de ejecucion -> Reiniciar sesion* y volver a ejecutarla.
4. Celda **3** (Progreso, solo lectura): cuantas de las 112 estan completas y cuales faltan. La celda **2** (Auditoria) es opcional.
5. Celda **4** (Lanzamiento) con `SESION = "A"` y dejarla. Segunda pestana: `SESION = "B"`. Nunca la misma sesion en dos pestanas. Para lotes mas chicos: `LOTE = "T2"`, `"T3-fcnn"`, `"T3-lstm_resid"`, `"T3-ensemble_stl"` o `"T3-lstm_direct"`.

**Si se corta** (desconexion, 12 h, falta de RAM): *Reiniciar sesion*, celda 1 y celda 4 con la misma `SESION` y `LOTE`. Lo completo se salta; lo parcial continua desde la ultima region guardada; nada se repite.

## PC

Un unico **supervisor** (`scripts/cola_local.py`, entorno `.venv_local`) corre en segundo plano y no depende de ninguna sesion de chat:

Lanzarlo **por WMI** (el proceso queda fuera del árbol de la aplicación que lo invoca). Con `Start-Process` el supervisor y sus workers morían al reiniciarse la app de Claude (2026-10-20 11:07, `KeyboardInterrupt`):

```powershell
$raiz = "C:\Users\HP\Documents\Tesis Claude"
$cmd = '"' + $raiz + '\.venv_local\Scripts\pythonw.exe" "' + $raiz + '\scripts\cola_local.py"'
$si = New-CimInstance -ClassName Win32_ProcessStartup -ClientOnly -Property @{ShowWindow=[uint16]0}
Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine=$cmd; CurrentDirectory=$raiz; ProcessStartupInformation=$si}
```

Comprobación: el proceso `pythonw.exe` del supervisor debe tener como padre a `WmiPrvSE` y no estar en ningún *job* de Windows.

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
