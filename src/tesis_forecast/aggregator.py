"""
Agregador de resultados: consolida las corridas ya producidas en
`Pipeline_Resultados/<RUN_NAME>/` en dos datasets planos pensados para
Looker Studio -- `metricas_master.csv` y `series_master.csv`.

Independiente del entrenamiento a proposito: no importa `runner.py` ni
ningun modulo de `models/` (esos arrastran tensorflow/optuna/lightgbm/
xgboost). Solo lee CSV/JSON ya escritos en disco -- pandas + `config.py`
(liviano) + `validator.py` (liviano) son las unicas dependencias del
proyecto. No entrena, no reejecuta, no modifica ni borra ninguna carpeta
de resultados: es de solo lectura sobre `Pipeline_Resultados/`, y solo
escribe los dos CSV maestros (por defecto, en la raiz de esa misma
carpeta, como archivos hermanos de las carpetas de corridas -- nunca dentro
de una carpeta de corrida).

Reejecutarlo es seguro e idempotente: cada llamada reconstruye los dos CSV
maestros DESDE CERO a partir del estado actual de `Pipeline_Resultados/`
(nunca lee/acumula su propia salida anterior), asi que no hay forma de que
una fila quede duplicada por correr esto varias veces -- el archivo de
salida simplemente se sobreescribe con el resultado fresco de releer todo.

Clasificacion de familia (1A/1B/individual/temp_igae/unknown): a partir de
`modelo` + `exogenas` de cada `config.json`, NUNCA del nombre de la
carpeta. Ver `clasificar_familia()`.

Salida: `Pipeline_Resultados/Consolidado/` (subcarpeta dedicada, separada
de las carpetas de corridas -- `descubrir_runs_completos()` la excluye
explicitamente del descubrimiento para que nunca se intente leer como si
fuera una corrida).
"""

import os
import json
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

from .config import MODEL_LABELS
from .regions import REGIONS_ALL
from .validator import validar_resultado

# =========================================================
# CLASIFICACION DE FAMILIA (a partir de config, no de carpetas)
# =========================================================

# Mismos 12 modelos y el mismo agrupamiento 1A/1B que ya usa el resto del
# proyecto (ver runner.MODEL_RUNNERS, notebooks/run_matrix.ipynb). No se
# importa runner.py (pesado); en su lugar, el assert de abajo verifica en
# cada import que este agrupamiento sigue cubriendo exactamente los mismos
# modelos que config.MODEL_LABELS -- si alguien agrega un modelo 13 sin
# actualizar este archivo, falla aqui en vez de clasificar en silencio.
FAMILIA_1A_MODELOS = frozenset({"xgboost", "lightgbm", "lstm_direct", "sarimax", "fcnn", "ensemble_stl"})
FAMILIA_1B_MODELOS = frozenset({"naive", "naive_trend", "naive_trend_seasonal", "ar", "ar_resid_trend_seasonal", "lstm_resid"})

_modelos_clasificados = FAMILIA_1A_MODELOS | FAMILIA_1B_MODELOS
_modelos_registrados = set(MODEL_LABELS)
if _modelos_clasificados != _modelos_registrados:
    raise RuntimeError(
        "aggregator.py desactualizado respecto a config.MODEL_LABELS: "
        f"en MODEL_LABELS pero no clasificados aqui: {_modelos_registrados - _modelos_clasificados}; "
        f"clasificados aqui pero ya no en MODEL_LABELS: {_modelos_clasificados - _modelos_registrados}"
    )


FAMILIA_TEMP_IGAE_EXOGENAS = frozenset({"Temperatura", "IGAE"})


def clasificar_familia(modelo: str, exogenas: list):
    """
    Reglas evaluadas EN ESTE ORDEN (el orden importa -- ver el aviso mas
    abajo sobre por que Temp+IGAE se chequea ANTES que 1A/1B, no despues):

      1. **Individual**: `exogenas` tiene **exactamente 1** elemento -- el
         patron exacto que produce `build_individual_exog_matrix()`
         (Fase 2). `exogena_individual` = esa unica exogena.
      2. **temp_igae**: `set(exogenas) == {"Temperatura", "IGAE"}` (2
         elementos, exactamente esas dos, en cualquier orden) -- el patron
         exacto de la Fase 3. `exogena_individual = None`.
      3. **1A / 1B**: cualquier otro conjunto de exogenas (tipicamente el
         catalogo completo por defecto del modelo, 8 o 5 segun cual, o
         `[]` para univariados) -- "1A" si `modelo` esta en
         `FAMILIA_1A_MODELOS`, "1B" si esta en `FAMILIA_1B_MODELOS`.
      4. **unknown**: nada de lo anterior aplica (modelo no reconocido, o
         una combinacion de exogenas que no corresponde a ninguna fase
         registrada) -- NUNCA se inventa una familia; se devuelve
         "unknown" explicitamente para que quien llame decida (reportar,
         excluir, o incluir igual marcado como tal).

    IMPORTANTE (pedido explicito): el chequeo de `temp_igae` va ANTES del
    chequeo por modelo (1A/1B) a proposito. Si se invirtiera el orden,
    una corrida de `xgboost` con `exogenas=["Temperatura","IGAE"]` (Fase
    3) clasificaria como "1A" solo porque `xgboost` esta en
    `FAMILIA_1A_MODELOS` -- el modelo por si solo NO alcanza para decidir
    la familia, hace falta mirar las exogenas primero.

    Devuelve `(familia: str, exogena_individual: Optional[str])`.
    """
    exogenas = list(exogenas) if exogenas else []

    if len(exogenas) == 1:
        return "individual", exogenas[0]

    if set(exogenas) == FAMILIA_TEMP_IGAE_EXOGENAS:
        return "temp_igae", None

    if modelo in FAMILIA_1A_MODELOS:
        return "1A", None

    if modelo in FAMILIA_1B_MODELOS:
        return "1B", None

    return "unknown", None


# =========================================================
# DESCUBRIR CORRIDAS COMPLETAS
# =========================================================

# Nombre de la subcarpeta de salida (ver consolidar_resultados()). Excluida
# EXPLICITAMENTE del descubrimiento -- nunca se intenta leer como si fuera
# una carpeta de corrida, sin importar que contenga.
NOMBRE_CARPETA_CONSOLIDADO = "Consolidado"


@dataclass
class RunInfo:
    run_dir: str
    run_name: str
    modelo: str
    exogenas: list
    train_hours: object
    forecast_horizon: object
    optuna_n_trials: object
    seed: object
    notas: str
    git_commit: object
    generated_at: object
    familia_experimento: str
    exogena_individual: Optional[str]


@dataclass
class CandidatoDescartado:
    """Una carpeta que se considero pero NO entro a los masters -- para `reporte_consolidacion.csv`."""
    nombre: str
    estado: str  # "sin_config" | "incompleto"
    razon: str


@dataclass
class DescubrimientoResultado:
    runs: list = field(default_factory=list)
    n_incompletos: int = 0
    n_sin_config: int = 0
    n_familia_unknown: int = 0
    incompletos: list = field(default_factory=list)  # [(run_name, problemas)]
    descartados: list = field(default_factory=list)  # list[CandidatoDescartado], sin_config + incompletos juntos


def descubrir_runs_completos(pipeline_resultados_dir: str, regiones_esperadas: Optional[list] = None) -> DescubrimientoResultado:
    """
    Recorre las subcarpetas INMEDIATAS de `pipeline_resultados_dir` (una
    por `RUN_NAME`), y para cada una:
      - si es `Consolidado/` (la carpeta de salida de este mismo modulo):
        se ignora sin contarla como candidata de ningun tipo;
      - si falta `config.json`: se cuenta como "sin config" y se ignora
        (no es una corrida, o quedo interrumpida antes de escribirlo);
      - si `validar_resultado()` (el mismo validador que ya usan
        `runner.run_experiment`/`matrix.run_matrix`) dice que esta
        incompleta: se cuenta y se ignora, guardando el motivo;
      - si esta completa: se lee `config.json`, se clasifica la familia
        (incluyendo "unknown" si no se puede determinar con seguridad --
        se incluye igual en `runs`, nunca se inventa una familia, pero
        tampoco se descarta el resultado por eso), y se agrega a `runs`.

    Nunca escribe ni borra nada. Es seguro llamarla mientras otras corridas
    siguen en progreso en otra sesion de Colab -- las incompletas
    simplemente no entran en el resultado.
    """
    resultado = DescubrimientoResultado()

    if not os.path.isdir(pipeline_resultados_dir):
        print(f"AVISO: {pipeline_resultados_dir} no existe o no es una carpeta -- no hay nada que consolidar.")
        return resultado

    nombres = sorted(
        n for n in os.listdir(pipeline_resultados_dir)
        if os.path.isdir(os.path.join(pipeline_resultados_dir, n)) and n != NOMBRE_CARPETA_CONSOLIDADO
    )

    for nombre in nombres:
        run_dir = os.path.join(pipeline_resultados_dir, nombre)
        config_path = os.path.join(run_dir, "config.json")

        if not os.path.exists(config_path):
            resultado.n_sin_config += 1
            resultado.descartados.append(CandidatoDescartado(nombre, "sin_config", "falta config.json"))
            continue

        reporte = validar_resultado(run_dir, regiones_esperadas=regiones_esperadas)
        if not reporte.es_completo:
            resultado.n_incompletos += 1
            resultado.incompletos.append((nombre, reporte.problemas))
            resultado.descartados.append(CandidatoDescartado(nombre, "incompleto", "; ".join(reporte.problemas)))
            continue

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception as e:
            resultado.n_incompletos += 1
            motivo = f"config.json ilegible: {e}"
            resultado.incompletos.append((nombre, [motivo]))
            resultado.descartados.append(CandidatoDescartado(nombre, "incompleto", motivo))
            continue

        modelo = cfg.get("modelo")
        exogenas = cfg.get("exogenas") or []
        familia, exogena_individual = clasificar_familia(modelo, exogenas)
        if familia == "unknown":
            resultado.n_familia_unknown += 1
            print(f"AVISO: {nombre} -- familia no determinable con seguridad (modelo={modelo!r}, exogenas={exogenas!r}). Incluida en los masters con familia_experimento='unknown'.")

        resultado.runs.append(RunInfo(
            run_dir=run_dir,
            run_name=cfg.get("run_name", nombre),
            modelo=modelo,
            exogenas=exogenas,
            train_hours=cfg.get("train_hours"),
            forecast_horizon=cfg.get("forecast_horizon"),
            optuna_n_trials=cfg.get("optuna_n_trials"),
            seed=cfg.get("seed"),
            notas=cfg.get("notas"),
            git_commit=cfg.get("git_commit"),
            generated_at=cfg.get("generated_at"),
            familia_experimento=familia,
            exogena_individual=exogena_individual,
        ))

    return resultado


def construir_reporte_consolidacion(descubrimiento: DescubrimientoResultado) -> pd.DataFrame:
    """
    Inventario de TODAS las carpetas consideradas (incluidas y excluidas),
    con columnas `run_name`, `familia`, `estado`, `incluido`, `razon`.
    Pensado para guardarse como `reporte_consolidacion.csv` -- la
    trazabilidad de que se incluyo/excluyo y por que, separada de los
    datos mismos de `metricas_master`/`series_master`.
    """
    filas = []

    for run in descubrimiento.runs:
        razon = "" if run.familia_experimento != "unknown" else (
            f"familia no determinable con seguridad (modelo={run.modelo!r}, exogenas={run.exogenas!r})"
        )
        filas.append({
            "run_name": run.run_name,
            "familia": run.familia_experimento,
            "estado": "completo",
            "incluido": True,
            "razon": razon,
        })

    for descartado in descubrimiento.descartados:
        filas.append({
            "run_name": descartado.nombre,
            "familia": None,
            "estado": descartado.estado,
            "incluido": False,
            "razon": descartado.razon,
        })

    columnas = ["run_name", "familia", "estado", "incluido", "razon"]
    if not filas:
        return pd.DataFrame(columns=columnas)

    df = pd.DataFrame(filas, columns=columnas)
    return df.sort_values("run_name").reset_index(drop=True)


# =========================================================
# UTILIDADES DE COLUMNAS (evitar colisiones con metadata nueva)
# =========================================================

_COLUMNAS_METADATA = [
    "run_name", "modelo", "familia_experimento", "exogenas", "exogena_individual",
    "train_hours", "forecast_horizon", "optuna_n_trials", "seed", "notas",
    "git_commit", "generated_at", "run_dir",
]


def _renombrar_modelo_original(df: pd.DataFrame) -> pd.DataFrame:
    """
    `series.csv`/`metricas.csv` YA traen una columna `modelo` propia (el
    nombre interno de cada pipeline, ej. "XGBoost_Tuned_2Semanas",
    "STL_FCNN_Multivariada_Residuos_EXOG_Lag168", o "real" para las filas
    de la serie real) -- distinta del `modelo` canonico que pide esta
    tarea (ej. "xgboost", "fcnn", el mismo identificador de
    `ExperimentConfig.modelo`/`runner.MODEL_RUNNERS`). Se preserva esa
    columna original bajo `modelo_estrategia` (no se descarta informacion:
    es lo unico que distingue, por ejemplo, las 2 estrategias de FCNN
    dentro de una misma corrida) y se deja `modelo` libre para la
    metadata nueva.
    """
    df = df.copy()
    if "modelo" in df.columns:
        df = df.rename(columns={"modelo": "modelo_estrategia"})
    return df


def _evitar_colision_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ademas de `modelo` (manejado aparte, ver `_renombrar_modelo_original`),
    al menos un modulo (`sarimax_model.py`) ya escribe su propia columna
    `exogenas` en `metricas.csv` (los nombres INTERNOS que usa esa celda,
    ej. "['Temperaturas', 'IGAE', ...]") -- si se dejara tal cual,
    quedaria pisada por la columna `exogenas` nueva (el catalogo CANONICO
    de la config). Cualquier columna original cuyo nombre coincida con una
    columna de metadata nueva se renombra con sufijo `_original`, sin
    tocar su contenido.
    """
    df = df.copy()
    renombres = {
        col: f"{col}_original"
        for col in _COLUMNAS_METADATA
        if col in df.columns and col != "modelo"
    }
    return df.rename(columns=renombres) if renombres else df


def _agregar_metadata(df: pd.DataFrame, run: RunInfo) -> pd.DataFrame:
    df = df.copy()
    df["run_name"] = run.run_name
    df["modelo"] = run.modelo
    df["familia_experimento"] = run.familia_experimento
    df["exogenas"] = "|".join(run.exogenas)
    df["exogena_individual"] = run.exogena_individual
    df["train_hours"] = run.train_hours
    df["forecast_horizon"] = run.forecast_horizon
    df["optuna_n_trials"] = run.optuna_n_trials
    df["seed"] = run.seed
    df["notas"] = run.notas
    df["git_commit"] = run.git_commit
    df["generated_at"] = run.generated_at
    df["run_dir"] = run.run_dir
    return df


# =========================================================
# metricas_master.csv
# =========================================================

def construir_metricas_master(runs: list) -> pd.DataFrame:
    """
    Une `metricas.csv` de cada corrida COMPLETA (`runs`, ya filtradas por
    `descubrir_runs_completos`), preservando la granularidad original
    (una fila = una fila de metricas por region/modelo -- FCNN sigue
    aportando 2 filas por region, una por estrategia). No se recalcula
    ni se toca ningun valor de MAE/RMSE/MAPE/sMAPE; solo se le agregan
    columnas de metadata.

    Columnas heterogeneas entre modelos (ej. `AIC`/`BIC`/`order` solo en
    SARIMAX, `tuneado`/`horizonte_usado` solo en XGBoost/LightGBM/LSTM
    directa/Naive-family) se preservan tal cual via union de columnas
    (`pd.concat` con relleno `NaN` donde no aplique) -- ninguna se
    descarta ni se fuerza a un esquema comun.
    """
    frames = []

    for run in runs:
        metricas_path = os.path.join(run.run_dir, "metricas.csv")
        if not os.path.exists(metricas_path):
            print(f"AVISO: {run.run_name} paso validar_resultado() pero no tiene metricas.csv -- se omite.")
            continue

        try:
            df = pd.read_csv(metricas_path, encoding="utf-8-sig")
        except Exception as e:
            print(f"AVISO: no se pudo leer metricas.csv de {run.run_name}: {e} -- se omite.")
            continue

        df = _renombrar_modelo_original(df)
        df = _evitar_colision_metadata(df)
        df = _agregar_metadata(df, run)

        frames.append(df)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True, sort=False)


# =========================================================
# series_master.csv
# =========================================================

_TIPOS_COMPARABLES = {"real", "prediccion"}


def construir_series_master(runs: list, verbose: bool = True) -> pd.DataFrame:
    """
    Consolida `series.csv` de cada corrida completa en un unico dataset
    "largo" (una fila por timestamp/region/modelo), pensado para comparar
    predicciones de distintos modelos en Looker Studio SIN repetir
    innecesariamente la serie real:

      1. Se descartan filas `tipo == "componente_pred"` (desglose interno
         de Ensemble STL -- trend/seasonal/resid por separado, no es la
         prediccion final comparable).
      2. Las filas `tipo == "prediccion"` se conservan TODAS, una por cada
         corrida/modelo (eso es exactamente lo que hay que comparar).
      3. El "horizonte comparable" por region se determina a partir de los
         RESULTADOS -- la union de todos los timestamps que aparecen como
         `prediccion` en CUALQUIER corrida para esa region -- no de
         `train_hours`/`forecast_horizon` de la config (que ademas puede
         ser el string "auto" para Naive/Naive_Trend/AR, sin un numero
         fijo de horas que asumir).
      4. Las filas `tipo == "real"` (que cada modulo guarda con la serie
         COMPLETA, no solo la ventana de test -- ver docstring de
         `fcnn_model.py`/`sarimax_model.py`/etc.) se recortan a solo esos
         timestamps comparables, y se deduplican por `(region, timestamp)`
         -- el mismo dato real no se repite una vez por cada corrida que
         lo tenia guardado.

    Si dos corridas traen un valor "real" distinto para el mismo
    `(region, timestamp)` (evidencia de que corrieron contra snapshots de
    datos distintos), se imprime un aviso y se conserva el primer valor
    visto -- no se promedia ni se descarta silenciosamente.

    Las filas `real` no pertenecen a ninguna corrida en particular, asi que
    sus columnas de metadata por-corrida (`run_name`, `modelo`,
    `familia_experimento`, `exogenas`, `exogena_individual`) quedan en
    `NaN`; `modelo_estrategia` conserva el valor original ("real") para
    que `serie_tipo`/`modelo_estrategia` sigan siendo suficientes para
    filtrar sin depender de que las demas columnas esten vacias.
    """
    pred_frames = []
    real_candidatos = []  # lista de DataFrames crudos (region, timestamp, valor), 1 por corrida que trajo "real"

    ventanas_test_por_region = {}  # region -> lista de (run_name, min_ts, max_ts, n_timestamps)

    for run in runs:
        series_path = os.path.join(run.run_dir, "series.csv")
        if not os.path.exists(series_path):
            print(f"AVISO: {run.run_name} paso validar_resultado() pero no tiene series.csv -- se omite.")
            continue

        try:
            df = pd.read_csv(series_path, encoding="utf-8-sig")
        except Exception as e:
            print(f"AVISO: no se pudo leer series.csv de {run.run_name}: {e} -- se omite.")
            continue

        if "tipo" not in df.columns:
            print(f"AVISO: series.csv de {run.run_name} no tiene columna 'tipo' -- se omite.")
            continue

        df = df[df["tipo"].isin(_TIPOS_COMPARABLES)].copy()
        if len(df) == 0:
            continue

        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
        df = _renombrar_modelo_original(df)
        df = df.rename(columns={"fecha": "timestamp", "tipo": "serie_tipo"})

        pred = df[df["serie_tipo"] == "prediccion"]
        real = df[df["serie_tipo"] == "real"]

        if len(pred) > 0:
            pred_tagged = _evitar_colision_metadata(pred)
            pred_tagged = _agregar_metadata(pred_tagged, run)
            pred_frames.append(pred_tagged)

            for region, grupo in pred.groupby("region"):
                ts = grupo["timestamp"]
                ventanas_test_por_region.setdefault(region, []).append(
                    (run.run_name, ts.min(), ts.max(), ts.nunique())
                )

        if len(real) > 0:
            real_candidatos.append(real[["region", "timestamp", "valor", "modelo_estrategia"]])

    if verbose:
        _reportar_ventanas_test(ventanas_test_por_region)

    pred_master = pd.concat(pred_frames, ignore_index=True, sort=False) if pred_frames else pd.DataFrame()

    real_master = _construir_real_deduplicado(real_candidatos, pred_master, verbose=verbose)

    columnas_metadata_real = [c for c in _COLUMNAS_METADATA if c != "modelo"]
    for col in columnas_metadata_real:
        if col not in real_master.columns:
            real_master[col] = np.nan
    real_master["modelo"] = np.nan

    columnas_finales = ["timestamp", "region", "valor", "serie_tipo", "modelo_estrategia"] + _COLUMNAS_METADATA
    for df in (real_master, pred_master):
        for col in columnas_finales:
            if col not in df.columns:
                df[col] = np.nan

    frames_finales = [d for d in (real_master, pred_master) if len(d) > 0]
    if not frames_finales:
        return pd.DataFrame(columns=columnas_finales)

    resultado = pd.concat([d[columnas_finales] for d in frames_finales], ignore_index=True, sort=False)
    return resultado.sort_values(["region", "timestamp", "serie_tipo", "run_name"], na_position="first").reset_index(drop=True)


def _construir_real_deduplicado(real_candidatos: list, pred_master: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    if not real_candidatos or len(pred_master) == 0:
        return pd.DataFrame(columns=["timestamp", "region", "valor", "serie_tipo", "modelo_estrategia"])

    timestamps_comparables = (
        pred_master[["region", "timestamp"]].drop_duplicates()
    )

    real_todo = pd.concat(real_candidatos, ignore_index=True, sort=False)
    real_todo = real_todo.dropna(subset=["timestamp"])

    real_recortado = real_todo.merge(timestamps_comparables, on=["region", "timestamp"], how="inner")

    if len(real_recortado) == 0:
        return pd.DataFrame(columns=["timestamp", "region", "valor", "serie_tipo", "modelo_estrategia"])

    conflictos = (
        real_recortado.groupby(["region", "timestamp"])["valor"]
        .agg(lambda s: s.max() - s.min() if len(s) > 1 else 0.0)
    )
    n_conflictos = int((conflictos.abs() > 1e-6).sum())
    if verbose and n_conflictos > 0:
        print(
            f"AVISO: {n_conflictos} (region, timestamp) tienen valores 'real' distintos entre corridas "
            "-- probablemente corrieron contra snapshots de datos distintos. Se conserva el primer valor visto."
        )

    real_dedup = real_recortado.drop_duplicates(subset=["region", "timestamp"], keep="first").copy()
    real_dedup["serie_tipo"] = "real"
    return real_dedup


def _reportar_ventanas_test(ventanas_test_por_region: dict):
    """
    Imprime, por region, si todas las corridas comparten exactamente el
    mismo rango de timestamps de test o no -- pedido explicito de la
    tarea ("verifica especialmente si todos los runs usan exactamente los
    mismos timestamps de test por region"). No fuerza nada: el join real
    ya esta disenado como union (`_construir_real_deduplicado`), asi que
    esto es puramente informativo.
    """
    if not ventanas_test_por_region:
        return

    print("\nVentanas de prediccion (horizonte de test) por region:")
    for region in sorted(ventanas_test_por_region):
        entradas = ventanas_test_por_region[region]
        rangos = {(str(min_ts), str(max_ts), n) for _, min_ts, max_ts, n in entradas}

        if len(rangos) == 1:
            (min_ts, max_ts, n) = next(iter(rangos))
            print(f"  {region}: {len(entradas)} corrida(s), TODAS con el mismo rango [{min_ts} .. {max_ts}] ({n} horas)")
        else:
            print(f"  {region}: {len(entradas)} corrida(s) con rangos DISTINTOS de test -- no se asume alineacion:")
            for run_name, min_ts, max_ts, n in sorted(entradas, key=lambda t: t[0]):
                print(f"      {run_name}: [{min_ts} .. {max_ts}] ({n} horas)")


# =========================================================
# API DE ALTO NIVEL
# =========================================================

def consolidar_resultados(
    pipeline_resultados_dir: str,
    output_dir: Optional[str] = None,
    regiones_esperadas: Optional[list] = None,
    escribir_csv: bool = True,
    escribir_reporte: bool = True,
):
    """
    Punto de entrada unico: descubre las corridas completas, arma
    `metricas_master.csv`/`series_master.csv`/`reporte_consolidacion.csv`,
    y (si `escribir_csv=True`, default) los escribe en `output_dir` --
    por defecto, `pipeline_resultados_dir/Consolidado/` (subcarpeta
    dedicada, nunca mezclada con las carpetas de corridas: el propio
    `descubrir_runs_completos()` la excluye del descubrimiento). Solo
    lectura sobre las carpetas de corridas existentes; nunca las modifica
    ni las borra.

    Idempotente: cada llamada reconstruye todo desde `Pipeline_Resultados/`
    (nunca lee su propia salida anterior), asi que correrlo varias veces
    seguidas sobre los mismos resultados produce el mismo contenido, sin
    acumular ni duplicar nada.

    Devuelve `(metricas_df, series_df, descubrimiento)`.
    """
    output_dir = output_dir or os.path.join(pipeline_resultados_dir, NOMBRE_CARPETA_CONSOLIDADO)
    regiones_esperadas = list(regiones_esperadas) if regiones_esperadas is not None else list(REGIONS_ALL)

    descubrimiento = descubrir_runs_completos(pipeline_resultados_dir, regiones_esperadas=regiones_esperadas)

    print("=" * 80)
    print("CONSOLIDACION DE RESULTADOS")
    print("=" * 80)
    print(f"Carpeta: {pipeline_resultados_dir}")
    print(f"Salida:  {output_dir}")
    print(f"Corridas completas incluidas: {len(descubrimiento.runs)}")
    print(f"Corridas incompletas excluidas: {descubrimiento.n_incompletos}")
    print(f"Carpetas sin config.json excluidas: {descubrimiento.n_sin_config}")
    if descubrimiento.n_familia_unknown:
        print(f"AVISO: {descubrimiento.n_familia_unknown} corrida(s) con familia 'unknown' (incluidas igual, revisar modelo/exogenas)")

    if descubrimiento.incompletos:
        print("\nExcluidas por incompletas (motivo):")
        for run_name, problemas in descubrimiento.incompletos:
            print(f"  - {run_name}: {'; '.join(problemas)}")

    if descubrimiento.runs:
        por_familia = pd.Series([r.familia_experimento for r in descubrimiento.runs]).value_counts()
        print("\nCorridas completas por familia:")
        for familia, n in por_familia.items():
            print(f"  {familia}: {n}")

        por_modelo = pd.Series([r.modelo for r in descubrimiento.runs]).value_counts()
        print("\nCorridas completas por modelo:")
        for modelo, n in por_modelo.items():
            print(f"  {modelo}: {n}")

    metricas_df = construir_metricas_master(descubrimiento.runs)
    series_df = construir_series_master(descubrimiento.runs)
    reporte_df = construir_reporte_consolidacion(descubrimiento)

    print(f"\nmetricas_master: {len(metricas_df):,} filas")
    print(f"series_master:   {len(series_df):,} filas "
          f"({(series_df['serie_tipo'] == 'real').sum():,} real, {(series_df['serie_tipo'] == 'prediccion').sum():,} prediccion)"
          if len(series_df) else "")

    if escribir_csv:
        os.makedirs(output_dir, exist_ok=True)
        metricas_path = os.path.join(output_dir, "metricas_master.csv")
        series_path = os.path.join(output_dir, "series_master.csv")

        metricas_df.to_csv(metricas_path, index=False, encoding="utf-8-sig")
        series_df.to_csv(series_path, index=False, encoding="utf-8-sig")

        print(f"\nEscrito: {metricas_path}")
        print(f"Escrito: {series_path}")

        if escribir_reporte:
            reporte_path = os.path.join(output_dir, "reporte_consolidacion.csv")
            reporte_df.to_csv(reporte_path, index=False, encoding="utf-8-sig")
            print(f"Escrito: {reporte_path}")

    return metricas_df, series_df, descubrimiento
