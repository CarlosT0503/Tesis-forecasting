"""
Evita que Windows se suspenda por inactividad mientras haya procesos
`run_local_estadisticos.py` en ejecucion. No cambia ninguna configuracion de
energia: usa SetThreadExecutionState, que deja de aplicar cuando termina este
proceso. Cerrar la tapa o elegir Suspender si suspenden el equipo.
"""
import ctypes
import subprocess
import time

ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001


def hay_trabajo() -> bool:
    out = subprocess.run(
        ["wmic", "process", "where", "name='python.exe'", "get", "CommandLine"],
        capture_output=True, text=True,
    ).stdout
    return "run_local_estadisticos" in out


while True:
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)
    time.sleep(30)
    if not hay_trabajo():
        break
ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
