"""
Montaje de Google Drive y resolucion de la carpeta base de resultados.

En el notebook legacy, el pipeline de XGBoost (celda 49) escribia primero en
una carpeta local /content/drive "falsa" (creada por os.makedirs porque Drive
todavia no estaba montado), y una celda posterior (51) montaba Drive de verdad
y copiaba los resultados desde ahi. Ese parche ya no es necesario: aqui el
runner exige montar Drive ANTES de crear cualquier carpeta de resultados, asi
que el problema que la celda 51 corregia no vuelve a ocurrir.
"""

BASE_DIR = "/content/drive/MyDrive/Pipeline_Resultados"


def mount_drive() -> bool:
    """
    Monta Google Drive si estamos en Colab. Fuera de Colab es un no-op
    (permite probar el resto del pipeline localmente).
    """
    try:
        from google.colab import drive
    except ImportError:
        print("No se detecto Google Colab: se omite el montaje de Drive.")
        return False

    drive.mount("/content/drive")
    print("Google Drive montado correctamente.")
    return True


def resolve_base_dir() -> str:
    """Carpeta raiz de resultados, la misma que usaba el pipeline legacy."""
    return BASE_DIR
