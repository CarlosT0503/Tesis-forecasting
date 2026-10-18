import os
import sys
import subprocess

from google.colab import drive
drive.mount("/content/drive")

!pip install -q optuna lightgbm

REPO_URL = "https://github.com/CarlosT0503/Tesis-forecasting.git"
REPO_DIR = "/content/tesis_repo"
if not os.path.exists(REPO_DIR):
    !git clone {REPO_URL} {REPO_DIR}
else:
    !git -C {REPO_DIR} pull

SRC_DIR = os.path.join(REPO_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Rutas (deben coincidir con io_drive.py)
DATA_DIR = "/content/drive/MyDrive/Bases de datos Tesis"
ORIG_DIR = "/content/drive/MyDrive/Pipeline_Resultados"
VENT_DIR = "/content/drive/MyDrive/Pipeline_Resultados_Ventanas"
os.makedirs(os.path.join(VENT_DIR, "_auditoria"), exist_ok=True)

from tesis_forecast import io_drive, windows
from tesis_forecast import ventanas_tools as vt
from tesis_forecast.matrix import run_matrix, resumen_dataframe

commit = subprocess.run(["git", "-C", REPO_DIR, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
print("Version del repositorio:", commit)
assert io_drive.BASE_DIR_VENTANAS == VENT_DIR, "VENT_DIR no coincide con io_drive.BASE_DIR_VENTANAS"
assert io_drive.BASE_DIR == ORIG_DIR, "ORIG_DIR no coincide con io_drive.BASE_DIR"
assert hasattr(vt, "estado_plan") and "xgboost" in vt.MODELOS_LOCALES, "Codigo desactualizado: reinicia el entorno y vuelve a ejecutar esta celda"
print("Ventanas:", {k: (str(v.test_start), str(v.test_end)) for k, v in windows.VENTANAS.items()})
