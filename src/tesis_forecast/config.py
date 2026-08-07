"""
Configuracion de un experimento y generacion deterministica del RUN_NAME.

RUN_NAME = <Modelo>_train<horas>h_fh<horizonte>h_<exogenas>
Ejemplo:  XGBoost_train336h_fh168h_Temp-Prim-Sec-Terc-IGAE-Gen-Imp-Exp

Sin timestamp ni hash: el mismo conjunto de (modelo, train_hours,
forecast_horizon, exogenas) siempre produce el mismo nombre, y el runner se
niega a sobrescribir un RUN_NAME que ya exista en disco.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

# Modelos disponibles. Se agregan mas entradas conforme se vayan
# extrayendo LSTM directa, SARIMAX, FCNN y Ensemble del notebook legacy.
MODEL_LABELS = {
    "xgboost": "XGBoost",
}

# Catalogo de exogenas y su abreviatura para el RUN_NAME, en un orden fijo
# (independiente del orden en que el usuario las liste en ExperimentConfig).
EXOG_ABBR = {
    "Temperatura": "Temp",
    "Primarias": "Prim",
    "Secundarias": "Sec",
    "Terciarias": "Terc",
    "IGAE": "IGAE",
    "Generacion": "Gen",
    "Importacion": "Imp",
    "Exportacion": "Exp",
}


@dataclass
class ExperimentConfig:
    modelo: str
    exogenas: Optional[list] = None   # None -> usa el default vigente del modelo
    train_hours: Optional[int] = None
    forecast_horizon: Optional[int] = None
    optuna_n_trials: Optional[int] = None
    seed: int = 42
    notas: str = ""


def build_run_name(modelo: str, train_hours: int, forecast_horizon: int, exogenas: list) -> str:
    if modelo not in MODEL_LABELS:
        raise ValueError(f"Modelo desconocido: {modelo}")

    desconocidas = [e for e in exogenas if e not in EXOG_ABBR]
    if desconocidas:
        raise ValueError(f"Exogenas no reconocidas en el catalogo: {desconocidas}")

    slug = "-".join(abbr for nombre, abbr in EXOG_ABBR.items() if nombre in exogenas)

    return f"{MODEL_LABELS[modelo]}_train{train_hours}h_fh{forecast_horizon}h_{slug}"


def _git_commit() -> Optional[str]:
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()
        )
    except Exception:
        return None


def resolved_config_dict(
    config: ExperimentConfig,
    run_name: str,
    train_hours: int,
    forecast_horizon: int,
    optuna_n_trials: int,
    exogenas: list,
) -> dict:
    """Config completa a persistir en config.json, con todos los defaults ya resueltos."""
    return {
        "modelo": config.modelo,
        "exogenas": exogenas,
        "train_hours": train_hours,
        "forecast_horizon": forecast_horizon,
        "optuna_n_trials": optuna_n_trials,
        "seed": config.seed,
        "notas": config.notas,
        "run_name": run_name,
        "git_commit": _git_commit(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
