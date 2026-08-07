"""
Orquestador minimo de un experimento: resuelve defaults, arma el RUN_NAME,
crea la carpeta (o aborta si ya existe), monta Drive, corre el modelo, y
guarda config.json / series.csv / metricas.csv / trials.csv / config_usada.csv.

No hay matrices, scheduler ni infraestructura de nube todavia -- eso se
agrega despues, en modulos separados (matrix.py, validator.py, registry.py)
que se apoyan en las funciones de este archivo sin tener que tocarlas. Ver
docs/AUTOMATIZACION_FUTURA.md para el mapeo explicito entre cada capacidad
futura pedida y lo que ya existe aqui para soportarla.
"""

import contextlib
import json
import os
import sys
import traceback
from dataclasses import dataclass, field
from typing import Optional

from . import io_drive
from .config import ExperimentConfig, build_run_name, resolved_config_dict
from .data.exogenas import cargar_exogenas_horarias
from .models import xgboost_model
from .regions import REGIONS_ALL

MODEL_DEFAULTS = {
    "xgboost": {
        "train_hours": xgboost_model.TRAIN_LAST_HOURS_DEFAULT,
        "forecast_horizon": xgboost_model.FORECAST_HORIZON_DEFAULT,
        "optuna_n_trials": xgboost_model.N_TRIALS_OPTUNA_DEFAULT,
        "exogenas": xgboost_model.EXOG_COLS_DEFAULT,
        "catalogo": xgboost_model.EXOG_CATALOGO,
    },
}

MODEL_RUNNERS = {
    "xgboost": xgboost_model.run,
}


@dataclass
class ResolvedRun:
    """Config de un experimento con todos los defaults ya resueltos, y el
    RUN_NAME/ruta que le corresponden -- sin ejecutar nada ni tocar disco.

    Pensado para que una capa futura (deteccion de duplicados, matriz de
    experimentos) pueda calcular "que archivo le tocaria a esta config" sin
    tener que duplicar la logica de defaults que ya vive en run_experiment().
    """

    modelo: str
    run_name: str
    run_dir: str
    train_hours: int
    forecast_horizon: int
    optuna_n_trials: int
    exogenas: list


@dataclass
class ExperimentResult:
    """Resultado de una corrida completada con exito.

    run_experiment() sigue levantando una excepcion si algo falla (no
    devuelve un status="failed"); este objeto es el "caso feliz". Una capa
    futura que agregue resultados de varios experimentos en un resumen
    puede construir su propio registro con status="failed" a partir de la
    excepcion capturada, usando los mismos nombres de campo para que un
    resumen combinado sea consistente.
    """

    run_name: str
    run_dir: str
    status: str  # siempre "completed" cuando lo devuelve run_experiment()
    regiones_esperadas: int
    regiones_con_metricas: int
    mape_promedio: Optional[float]
    archivos: dict = field(default_factory=dict)


def resolve_run(config: ExperimentConfig) -> ResolvedRun:
    """
    Resuelve defaults + valida exogenas + calcula RUN_NAME y run_dir, sin
    efectos secundarios (no monta Drive, no crea carpetas, no entrena nada).

    Util para que un futuro matrix runner pueda decidir "esta config ya
    existe, la salto" ANTES de invertir tiempo de computo, simplemente
    llamando experiment_exists(config).
    """
    if config.modelo not in MODEL_RUNNERS:
        raise ValueError(
            f"Modelo '{config.modelo}' todavia no esta extraido al pipeline nuevo. "
            f"Disponibles: {list(MODEL_RUNNERS)}"
        )

    defaults = MODEL_DEFAULTS[config.modelo]

    train_hours = config.train_hours if config.train_hours is not None else defaults["train_hours"]
    forecast_horizon = (
        config.forecast_horizon if config.forecast_horizon is not None else defaults["forecast_horizon"]
    )
    optuna_n_trials = (
        config.optuna_n_trials if config.optuna_n_trials is not None else defaults["optuna_n_trials"]
    )
    exogenas = config.exogenas if config.exogenas is not None else list(defaults["exogenas"])

    desconocidas = [e for e in exogenas if e not in defaults["catalogo"]]
    if desconocidas:
        raise ValueError(
            f"El modelo '{config.modelo}' no sabe tratar estas exogenas: {desconocidas}. "
            f"Catalogo permitido: {defaults['catalogo']}"
        )

    run_name = build_run_name(config.modelo, train_hours, forecast_horizon, exogenas)
    run_dir = os.path.join(io_drive.resolve_base_dir(), run_name)

    return ResolvedRun(
        modelo=config.modelo,
        run_name=run_name,
        run_dir=run_dir,
        train_hours=train_hours,
        forecast_horizon=forecast_horizon,
        optuna_n_trials=optuna_n_trials,
        exogenas=exogenas,
    )


def experiment_exists(config: ExperimentConfig) -> bool:
    """
    True si ya existe una carpeta de resultados para este RUN_NAME.

    Importante: requiere que Google Drive ya este montado en esta sesion de
    Colab (drive.mount ya corrido, por ejemplo en la celda de setup del
    notebook, o pasando mount_drive=True en una llamada previa a
    run_experiment). Si Drive no esta montado, esta funcion no puede ver el
    contenido real de Drive y siempre devuelve False -- un falso negativo,
    no una confirmacion de que el experimento no existe.
    """
    resolved = resolve_run(config)
    return os.path.exists(resolved.run_dir)


class _Tee:
    """Duplica escrituras de texto a varios streams a la vez (usado para que
    todo lo impreso durante el pipeline quede tambien en log.txt, ademas de
    en la salida normal de la celda de Colab)."""

    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for s in self.streams:
            s.write(data)

    def flush(self):
        for s in self.streams:
            s.flush()


@contextlib.contextmanager
def _tee_stdout_to_file(path):
    log_file = open(path, "a", encoding="utf-8")
    original_stdout = sys.stdout
    sys.stdout = _Tee(original_stdout, log_file)
    try:
        yield
    finally:
        sys.stdout = original_stdout
        log_file.close()


def run_experiment(
    config: ExperimentConfig,
    data_dir: str = "/content",
    mount_drive: bool = True,
) -> ExperimentResult:
    resolved = resolve_run(config)
    run_name = resolved.run_name
    run_dir = resolved.run_dir
    train_hours = resolved.train_hours
    forecast_horizon = resolved.forecast_horizon
    optuna_n_trials = resolved.optuna_n_trials
    exogenas = resolved.exogenas

    if mount_drive:
        io_drive.mount_drive()

    if os.path.exists(run_dir):
        raise FileExistsError(
            f"Ya existe un experimento con este RUN_NAME:\n{run_dir}\n"
            "No se sobrescribe. Borralo manualmente si de verdad quieres repetirlo "
            "(mas adelante se puede agregar un flag explicito de overwrite)."
        )

    os.makedirs(run_dir)

    resolved_cfg = resolved_config_dict(config, run_name, train_hours, forecast_horizon, optuna_n_trials, exogenas)
    with open(os.path.join(run_dir, "config.json"), "w", encoding="utf-8") as f:
        json.dump(resolved_cfg, f, indent=2, ensure_ascii=False)

    # log.txt: todo lo que el pipeline imprime durante esta corrida (mismos
    # prints que ya existian en xgboost_model.py, no se agrego ningun print
    # nuevo alli) mas el traceback completo si la corrida falla. Es lo que
    # permite revisar despues -- o que un agente inspeccione -- que paso en
    # una corrida nocturna sin que nadie haya estado mirando la pantalla.
    log_path = os.path.join(run_dir, "log.txt")

    try:
        with _tee_stdout_to_file(log_path):
            print(f"Experimento: {run_name}")
            print(f"Resultados en: {run_dir}")

            exogenas_globales = cargar_exogenas_horarias(data_dir=data_dir)

            modelo_run = MODEL_RUNNERS[config.modelo]
            series_df, metricas_df, trials_df, config_usada_df = modelo_run(
                exogenas_globales=exogenas_globales,
                regions_all=REGIONS_ALL,
                train_hours=train_hours,
                forecast_horizon=forecast_horizon,
                exog_cols=exogenas,
                optuna_n_trials=optuna_n_trials,
                data_dir=data_dir,
                output_dir=run_dir,
            )

            # Guardado final (el pipeline ya guardo avances incrementales por
            # region; esto asegura que el csv final refleje exactamente lo
            # que se devolvio). metricas.csv (desempeno) y config_usada.csv
            # (mejores hiperparametros por region) se guardan por separado a
            # proposito: uno describe que tan bien predijo el modelo, el
            # otro con que hiperparametros se logro.
            archivos = {"config": os.path.join(run_dir, "config.json")}

            series_df.to_csv(os.path.join(run_dir, "series.csv"), index=False, encoding="utf-8-sig")
            archivos["series"] = os.path.join(run_dir, "series.csv")

            metricas_df.to_csv(os.path.join(run_dir, "metricas.csv"), index=False, encoding="utf-8-sig")
            archivos["metricas"] = os.path.join(run_dir, "metricas.csv")

            if trials_df is not None and len(trials_df) > 0:
                trials_df.to_csv(os.path.join(run_dir, "trials.csv"), index=False, encoding="utf-8-sig")
                archivos["trials"] = os.path.join(run_dir, "trials.csv")

            if config_usada_df is not None and len(config_usada_df) > 0:
                config_usada_df.to_csv(os.path.join(run_dir, "config_usada.csv"), index=False, encoding="utf-8-sig")
                archivos["config_usada"] = os.path.join(run_dir, "config_usada.csv")

            archivos["log"] = log_path

            print("\nExperimento completado.")
            for nombre_archivo, ruta in archivos.items():
                print(f"  {nombre_archivo}: {ruta}")

    except Exception:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("\n\n" + "=" * 80 + "\n")
            f.write("ERROR: la corrida no completo\n")
            f.write("=" * 80 + "\n")
            f.write(traceback.format_exc())
        raise

    mape_promedio = None
    if len(metricas_df) > 0 and "MAPE" in metricas_df.columns:
        mape_promedio = float(metricas_df["MAPE"].mean())

    return ExperimentResult(
        run_name=run_name,
        run_dir=run_dir,
        status="completed",
        regiones_esperadas=len(REGIONS_ALL),
        regiones_con_metricas=len(metricas_df),
        mape_promedio=mape_promedio,
        archivos=archivos,
    )
