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

Clasificacion de familia (1A/1B/individual/temp_igae/univariado/unknown): a
partir de `modelo` + `exogenas` de cada `config.json`, NUNCA del nombre de
la carpeta. Ver `clasificar_familia()`. La familia `univariado` es la unica
excepcion: no viene de un `config.json` (esas corridas no tienen uno --
son legacy, de un script/notebook anterior a `runner.py`), se asigna
directamente al importar `Legacy_Univariados/` -- ver
`procesar_legacy_univariado()`.

Salida: `Pipeline_Resultados/Consolidado/` (subcarpeta dedicada, separada
de las carpetas de corridas -- `descubrir_runs_completos()` la excluye
explicitamente del descubrimiento para que nunca se intente leer como si
fuera una corrida). `Pipeline_Resultados/Legacy_Univariados/` (los 2 CSV
legacy) tambien se excluye del descubrimiento por el mismo motivo: no es
una carpeta de corrida moderna, se integra por una ruta explicita via
`consolidar_resultados(legacy_metricas_path=..., legacy_series_path=...)`.
"""

import os
import json
import re
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

# Nombre de la subcarpeta legacy (metricas_global.csv/series_global.csv).
# Excluida del descubrimiento por el MISMO mecanismo que Consolidado/: no
# tiene config.json (nunca lo tuvo, es de un script anterior a runner.py),
# asi que sin esta exclusion caeria en la rama "sin_config" y se reportaria
# como una carpeta descartada por error -- no es una corrida incompleta, es
# una fuente legacy valida que se integra por ruta explicita (ver
# procesar_legacy_univariado()/consolidar_resultados()).
NOMBRE_CARPETA_LEGACY_UNIVARIADO = "Legacy_Univariados"

_CARPETAS_NO_RUN = frozenset({NOMBRE_CARPETA_CONSOLIDADO, NOMBRE_CARPETA_LEGACY_UNIVARIADO})


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
      - si es `Consolidado/` o `Legacy_Univariados/` (la carpeta de salida
        de este mismo modulo, o la carpeta de los CSV legacy univariados):
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
        if os.path.isdir(os.path.join(pipeline_resultados_dir, n)) and n not in _CARPETAS_NO_RUN
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


def construir_reporte_consolidacion(
    descubrimiento: DescubrimientoResultado,
    ventanas_por_run: Optional[dict] = None,
    entradas_legacy: Optional[list] = None,
) -> pd.DataFrame:
    """
    Inventario de TODAS las carpetas/fuentes consideradas (incluidas y
    excluidas, modernas y legacy), con columnas `run_name`, `familia`,
    `origen` ("moderno" | "legacy_univariado"), `estado`, `incluido`,
    `razon`, `regiones`, `test_start`, `test_end`, `n_predicciones`.
    Pensado para guardarse como `reporte_consolidacion.csv` -- la
    trazabilidad de que se incluyo/excluyo y por que, separada de los
    datos mismos de `metricas_master`/`series_master`.

    `ventanas_por_run`: dict opcional `run_name -> {"regiones", "test_start",
    "test_end", "n_predicciones"}` (ver `calcular_ventanas_por_run()`
    agregado por run_name) -- si se pasa, rellena esas 4 columnas para
    CUALQUIER run_name presente ahi (moderno o legacy), derivado unicamente
    de lo que ya quedo en `series_master` (nunca recalculado aca).

    `entradas_legacy`: lista opcional de dicts (una por estrategia legacy
    procesada, ver `procesar_legacy_univariado()`) con
    `run_name`/`familia`/`estado`/`incluido`/`razon` -- se agregan tal cual,
    con `origen="legacy_univariado"`, sin tocar la logica de arriba (que
    sigue siendo exclusivamente sobre `descubrimiento`, corridas modernas).
    """
    filas = []
    ventanas_por_run = ventanas_por_run or {}

    def _fila_ventana(run_name):
        v = ventanas_por_run.get(run_name)
        if not v:
            return {"regiones": None, "test_start": None, "test_end": None, "n_predicciones": None}
        return {
            "regiones": "|".join(v.get("regiones") or []),
            "test_start": v.get("test_start"),
            "test_end": v.get("test_end"),
            "n_predicciones": v.get("n_predicciones"),
        }

    for run in descubrimiento.runs:
        razon = "" if run.familia_experimento != "unknown" else (
            f"familia no determinable con seguridad (modelo={run.modelo!r}, exogenas={run.exogenas!r})"
        )
        filas.append({
            "run_name": run.run_name,
            "familia": run.familia_experimento,
            "origen": "moderno",
            "estado": "completo",
            "incluido": True,
            "razon": razon,
            **_fila_ventana(run.run_name),
        })

    for descartado in descubrimiento.descartados:
        filas.append({
            "run_name": descartado.nombre,
            "familia": None,
            "origen": "moderno",
            "estado": descartado.estado,
            "incluido": False,
            "razon": descartado.razon,
            **_fila_ventana(descartado.nombre),
        })

    for entrada in (entradas_legacy or []):
        filas.append({
            "run_name": entrada["run_name"],
            "familia": entrada.get("familia", FAMILIA_UNIVARIADO),
            "origen": "legacy_univariado",
            "estado": entrada.get("estado", "completo"),
            "incluido": entrada.get("incluido", True),
            "razon": entrada.get("razon", ""),
            **_fila_ventana(entrada["run_name"]),
        })

    columnas = [
        "run_name", "familia", "origen", "estado", "incluido", "razon",
        "regiones", "test_start", "test_end", "n_predicciones",
    ]
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


def construir_series_master(
    runs: list,
    verbose: bool = True,
    extra_pred_frames: Optional[list] = None,
    extra_real_frames: Optional[list] = None,
) -> pd.DataFrame:
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

    `extra_pred_frames`/`extra_real_frames` (opcionales, default `None` ->
    comportamiento IDENTICO al de antes): fuentes adicionales YA taggeadas
    con su propio `run_name`/metadata (ej. `Legacy_Univariados/`, ver
    `procesar_legacy_univariado()`), que se suman al MISMO pool de
    predicciones/reales de las corridas modernas antes del merge y la
    deduplicacion -- reutilizan exactamente la misma logica de union de
    horizonte comparable, dedup de `real` y deteccion de conflictos que ya
    corre para corridas modernas, sin duplicar esa logica.
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

    # Fuentes adicionales (ej. legacy univariado) -- ya vienen taggeadas con
    # su propio run_name/modelo_estrategia; se suman tal cual al mismo pool,
    # SIN tocar nada de la logica de arriba (corridas modernas).
    for pred_extra in (extra_pred_frames or []):
        if pred_extra is None or len(pred_extra) == 0:
            continue
        pred_frames.append(pred_extra)
        for (region, run_name_extra), grupo in pred_extra.groupby(["region", "run_name"]):
            ts = grupo["timestamp"]
            ventanas_test_por_region.setdefault(region, []).append(
                (run_name_extra, ts.min(), ts.max(), ts.nunique())
            )

    for real_extra in (extra_real_frames or []):
        if real_extra is None or len(real_extra) == 0:
            continue
        real_candidatos.append(real_extra[["region", "timestamp", "valor", "modelo_estrategia"]])

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
# VENTANAS TEMPORALES POR RUN (test_start/test_end/n_predicciones)
# =========================================================

def calcular_ventanas_por_run(series_master_df: pd.DataFrame) -> pd.DataFrame:
    """
    A partir de series_master YA construido (moderno, o moderno+legacy),
    deriva por (run_name, region) la ventana de prediccion comparable
    (test_start/test_end) y el numero de predicciones -- unicamente de lo
    que ya quedo en series_master, sin recalcular nada ni asumir un
    horizonte fijo. No fuerza alineacion entre corridas: cada (run_name,
    region) conserva su propia ventana tal cual salio de sus predicciones.

    Pensada para analisis posterior (ej. distinguir en Looker Studio "todos
    los resultados" vs "comparacion estrictamente por misma ventana
    temporal") -- NUNCA se usa para recalcular metricas ni para forzar
    ninguna interseccion aca.
    """
    columnas = ["run_name", "region", "test_start", "test_end", "n_predicciones"]
    if len(series_master_df) == 0:
        return pd.DataFrame(columns=columnas)

    pred = series_master_df[series_master_df["serie_tipo"] == "prediccion"]
    pred = pred.dropna(subset=["run_name"])
    if len(pred) == 0:
        return pd.DataFrame(columns=columnas)

    agg = (
        pred.groupby(["run_name", "region"])["timestamp"]
        .agg(test_start="min", test_end="max", n_predicciones="count")
        .reset_index()
    )
    return agg[columnas]


def calcular_ventanas_agregadas_por_run(series_master_df: pd.DataFrame) -> dict:
    """
    Igual que `calcular_ventanas_por_run()` pero agregado por `run_name`
    solamente (union de todas sus regiones): `{run_name: {"regiones": [...],
    "test_start", "test_end", "n_predicciones"}}` -- el formato que espera
    `construir_reporte_consolidacion(ventanas_por_run=...)` (una fila por
    run_name, no por region).
    """
    por_region = calcular_ventanas_por_run(series_master_df)
    if len(por_region) == 0:
        return {}

    resultado = {}
    for run_name, grupo in por_region.groupby("run_name"):
        resultado[run_name] = {
            "regiones": sorted(grupo["region"].unique().tolist()),
            "test_start": grupo["test_start"].min(),
            "test_end": grupo["test_end"].max(),
            "n_predicciones": int(grupo["n_predicciones"].sum()),
        }
    return resultado


def agregar_ventanas_temporales(metricas_df: pd.DataFrame, series_master_df: pd.DataFrame) -> pd.DataFrame:
    """
    Enriquece metricas_master (SIN recalcular ningun MAE/RMSE/MAPE/sMAPE)
    con `test_start`/`test_end`/`n_predicciones` por (run_name, region),
    derivados de las predicciones ya presentes en series_master. Puramente
    aditivo (merge `how="left"`): una corrida sin predicciones comparables
    simplemente queda con esas 3 columnas en NaN/NaT.
    """
    columnas_nuevas = ["test_start", "test_end", "n_predicciones"]

    if len(metricas_df) == 0:
        out = metricas_df.copy()
        for col in columnas_nuevas:
            if col not in out.columns:
                out[col] = pd.Series(dtype="object")
        return out

    ventanas = calcular_ventanas_por_run(series_master_df)
    if len(ventanas) == 0:
        out = metricas_df.copy()
        for col in columnas_nuevas:
            out[col] = np.nan
        return out

    return metricas_df.merge(ventanas, on=["run_name", "region"], how="left")


# =========================================================
# LEGACY UNIVARIADO (Legacy_Univariados/metricas_global.csv +
# series_global.csv) -- integracion como quinta familia experimental
# =========================================================
#
# Estos 2 CSV NO vienen de runner.py (no tienen config.json, no siguen la
# convencion RUN_NAME=<Modelo>_train<h>h_fh<h>h_<exog>): son resultados de
# un script/notebook ANTERIOR, ya movidos a Drive tal cual. Esta seccion es
# la UNICA via de entrada para ellos -- nunca se descubren como carpeta
# (ver NOMBRE_CARPETA_LEGACY_UNIVARIADO en descubrir_runs_completos()), se
# integran por ruta EXPLICITA (ver consolidar_resultados(legacy_metricas_path=,
# legacy_series_path=)). Solo lectura sobre los 2 CSV: nunca se escriben,
# mueven ni sobreescriben.

FAMILIA_UNIVARIADO = "univariado"

# Tabla explicita estrategia_legacy -> modelo_canonico. Cada entrada esta
# documentada con la evidencia de codigo que la respalda -- NINGUNA es una
# adivinanza. Evidencia completa (ver tambien el reporte de auditoria
# entregado por separado):
#
#   - ENSEMBLE_STL_LSTMtrend_FCNNseason_ARresid:
#       models/ensemble_stl.py:124 -> NOMBRE_MODELO_FINAL =
#       "ENSEMBLE_STL_LSTMtrend_FCNNseason_ARresid_EXOG_ALL_Lag168" -- el
#       modulo MODERNO (multivariado) reutiliza EXACTAMENTE este nombre
#       como raiz y le agrega el sufijo de exogenas. La version legacy (sin
#       sufijo) es el equivalente UNIVARIADO -- distinto canonico porque es
#       una corrida distinta (script legacy, no ensemble_stl.py).
#   - ARIMA_1_1_1:
#       orden (1,1,1), sin estacionalidad ni exogenas -- no existe un
#       modulo moderno equivalente (sarimax_model.py ya es estacional Y
#       multivariado). Precursor simple de SARIMAX.
#   - SARIMA_1_1_1__1_0_1_168:
#       models/sarimax_model.py:427 -> NOMBRE_MODELO =
#       "SARIMAX_1_1_1__1_0_1_168_EXOG_2M" -- MISMO order=(1,1,1) y
#       seasonal_order=(1,0,1,168) (ver sarimax_model.py:63-64), version SIN
#       exogenas (SARIMA en vez de SARIMAX).
#   - FCNN_Individual:
#       analogo univariado de "FCNN_Multivariada_EXOG_Lag168"
#       (fcnn_model.py) -- sin modulo moderno univariado dedicado.
#   - STL_FCNN_residuos:
#       analogo univariado de "STL_FCNN_Multivariada_Residuos_EXOG_Lag168"
#       (fcnn_model.py) -- sin modulo moderno univariado dedicado.
#   - AR_AIC:
#       metodologia "orden AR elegido por AIC" -- coincide con
#       models/ar_model.py (docstring: "Seleccionando orden AR por AIC") Y
#       con models/ensemble_stl.py:905 ("resid_model": "AR_AIC", el AR
#       sobre el residuo dentro del ensemble). PERO ar_model.py moderno
#       guarda su metrica como "AR" (no "AR_AIC") -- no son la misma
#       corrida/modulo, por eso NO se reusa el canonico "ar" (reservado
#       para corridas modernas de ar_model.py).
#   - STL_AR_residuos_AIC:
#       analogo simplificado (STL + AR(AIC) sobre el residuo, SIN
#       tendencia lineal ni estacionalidad repetida reconstruidas aparte).
#       IMPORTANTE: el modulo moderno ar_resid_trend_seasonal_model.py es
#       EXPLICITAMENTE una "combinacion nueva" (ver config.py, docstring de
#       MODEL_LABELS: "no extraen un pipeline completo de legacy"), NO una
#       extraccion de esta estrategia legacy -- por eso NO comparten
#       canonico: metodologicamente son distintos, no serian comparables
#       como si fueran el mismo modelo.
#   - LSTM_Individual:
#       sin modulo moderno equivalente -- lstm_direct.py/lstm_resid_model.py
#       modernos son ambos multivariados (requieren exogenas, ver
#       config.py). Precursor univariado independiente.
MAPEO_ESTRATEGIA_LEGACY_UNIVARIADO = {
    "ENSEMBLE_STL_LSTMtrend_FCNNseason_ARresid": "ensemble_stl_univariado",
    "ARIMA_1_1_1": "arima",
    "SARIMA_1_1_1__1_0_1_168": "sarima",
    "FCNN_Individual": "fcnn_univariada",
    "STL_FCNN_residuos": "fcnn_residuos_stl",
    "AR_AIC": "ar_aic",
    "STL_AR_residuos_AIC": "ar_residuos_stl",
    "LSTM_Individual": "lstm_univariada",
}


def build_run_name_legacy_univariado(estrategia_legacy: str) -> str:
    """
    RUN_NAME deterministico para una estrategia legacy univariada: estable
    entre ejecuciones (depende solo del nombre de la estrategia, nunca del
    orden de lectura del CSV ni de un timestamp/hash), y estructuralmente
    no puede colisionar con ningun RUN_NAME moderno -- `build_run_name()`
    (config.py) siempre arranca con `MODEL_LABELS[modelo]` (ej. "XGBoost_",
    "SARIMAX_", "Naive_", ...), nunca con el prefijo fijo
    "Legacy_Univariado__" que se usa aca.
    """
    slug = re.sub(r"[^0-9A-Za-z_]+", "_", str(estrategia_legacy).strip())
    return f"Legacy_Univariado__{slug}"


def _derivar_region_desde_serie(nombre_serie) -> str:
    """Igual que `_region_de_serie()` en cada modulo de modelo/checkpoint.py: la region es el primer token de 'serie' (ej. 'BCA_DEMANDA' -> 'BCA')."""
    return str(nombre_serie).split("_")[0]


def _resolver_columna_region(df: pd.DataFrame, columna_serie: str = "serie") -> pd.Series:
    """
    Devuelve la columna 'region': si el CSV ya trae una columna 'region' la
    usa tal cual; si no, la deriva de 'serie' -- mismo criterio que usa el
    resto del proyecto (ver `_derivar_region_desde_serie`). Lanza un error
    claro (no adivina en silencio) si no hay forma segura de obtenerla.
    """
    if "region" in df.columns:
        return df["region"]
    if columna_serie not in df.columns:
        raise ValueError(
            f"No se pudo derivar 'region': el CSV no tiene columna 'region' ni '{columna_serie}'. "
            f"Columnas disponibles: {list(df.columns)}"
        )
    return df[columna_serie].map(_derivar_region_desde_serie)


@dataclass
class ValidacionLegacyUnivariado:
    """Resultado de `validar_legacy_univariado()` -- solo lectura, nunca modifica los CSV legacy."""
    ok: bool
    problemas: list
    regiones_metricas: list
    regiones_series: list
    estrategias_metricas: list
    estrategias_series_prediccion: list
    columnas_metricas: list
    columnas_series: list
    n_filas_metricas: int
    n_filas_series: int
    tipos_series: list
    tiene_real: bool
    tiene_componente_pred: bool
    n_predicciones_por_region_estrategia: dict
    ventana_prediccion_por_estrategia: dict
    estrategias_sin_mapeo: list


def validar_legacy_univariado(metricas_df: pd.DataFrame, series_df: pd.DataFrame) -> ValidacionLegacyUnivariado:
    """
    Validacion PREVIA, de solo lectura, de `metricas_global.csv`/
    `series_global.csv` YA LEIDOS en memoria (esta funcion no abre ni
    escribe ningun archivo). No hardcodea numeros esperados -- todo lo que
    reporta se deriva del contenido real de los DataFrames recibidos.
    """
    problemas = []

    columnas_metricas = list(metricas_df.columns)
    columnas_series = list(series_df.columns)

    for requerida in ["modelo", "MAE", "RMSE", "MAPE", "sMAPE"]:
        if requerida not in metricas_df.columns:
            problemas.append(f"metricas_global.csv: falta columna requerida '{requerida}'")

    for requerida in ["modelo", "fecha", "tipo", "valor"]:
        if requerida not in series_df.columns:
            problemas.append(f"series_global.csv: falta columna requerida '{requerida}'")

    if "region" not in metricas_df.columns and "serie" not in metricas_df.columns:
        problemas.append("metricas_global.csv: no tiene 'region' ni 'serie' -- no se puede derivar la region")
    if "region" not in series_df.columns and "serie" not in series_df.columns:
        problemas.append("series_global.csv: no tiene 'region' ni 'serie' -- no se puede derivar la region")

    if problemas:
        return ValidacionLegacyUnivariado(
            ok=False, problemas=problemas,
            regiones_metricas=[], regiones_series=[],
            estrategias_metricas=[], estrategias_series_prediccion=[],
            columnas_metricas=columnas_metricas, columnas_series=columnas_series,
            n_filas_metricas=len(metricas_df), n_filas_series=len(series_df),
            tipos_series=[], tiene_real=False, tiene_componente_pred=False,
            n_predicciones_por_region_estrategia={}, ventana_prediccion_por_estrategia={},
            estrategias_sin_mapeo=[],
        )

    region_metricas = _resolver_columna_region(metricas_df)
    region_series = _resolver_columna_region(series_df)

    regiones_metricas = sorted(region_metricas.dropna().unique().tolist())
    regiones_series = sorted(region_series.dropna().unique().tolist())

    estrategias_metricas = sorted(metricas_df["modelo"].dropna().unique().tolist())

    for col in ["MAE", "RMSE", "MAPE", "sMAPE"]:
        n_nan = int(metricas_df[col].isna().sum())
        if n_nan:
            problemas.append(f"metricas_global.csv: columna '{col}' tiene {n_nan} valor(es) NaN")

    tipos_series = sorted(series_df["tipo"].dropna().unique().tolist())
    tiene_real = "real" in tipos_series
    tiene_componente_pred = "componente_pred" in tipos_series

    pred_df = series_df[series_df["tipo"] == "prediccion"].copy()
    pred_df["region"] = _resolver_columna_region(pred_df)
    estrategias_series_prediccion = sorted(pred_df["modelo"].dropna().unique().tolist())

    n_predicciones_por_region_estrategia = pred_df.groupby(["region", "modelo"]).size().to_dict()

    fechas_pred = pd.to_datetime(pred_df["fecha"], errors="coerce")
    ventana_prediccion_por_estrategia = {}
    for estrategia, grupo in pred_df.assign(_fecha=fechas_pred).groupby("modelo"):
        ventana_prediccion_por_estrategia[estrategia] = (grupo["_fecha"].min(), grupo["_fecha"].max())

    estrategias_sin_mapeo = sorted(
        (set(estrategias_metricas) | set(estrategias_series_prediccion)) - set(MAPEO_ESTRATEGIA_LEGACY_UNIVARIADO)
    )
    if estrategias_sin_mapeo:
        problemas.append(
            f"Estrategias legacy SIN mapeo en MAPEO_ESTRATEGIA_LEGACY_UNIVARIADO -- se incluiran "
            f"con modelo=None, no se inventa un canonico: {estrategias_sin_mapeo}"
        )

    return ValidacionLegacyUnivariado(
        ok=True, problemas=problemas,
        regiones_metricas=regiones_metricas, regiones_series=regiones_series,
        estrategias_metricas=estrategias_metricas,
        estrategias_series_prediccion=estrategias_series_prediccion,
        columnas_metricas=columnas_metricas, columnas_series=columnas_series,
        n_filas_metricas=len(metricas_df), n_filas_series=len(series_df),
        tipos_series=tipos_series, tiene_real=tiene_real, tiene_componente_pred=tiene_componente_pred,
        n_predicciones_por_region_estrategia=n_predicciones_por_region_estrategia,
        ventana_prediccion_por_estrategia=ventana_prediccion_por_estrategia,
        estrategias_sin_mapeo=estrategias_sin_mapeo,
    )


def imprimir_validacion_legacy(validacion: ValidacionLegacyUnivariado):
    """Imprime el reporte de `validar_legacy_univariado()` en un formato legible -- pensado para la celda de diagnostico read-only en Colab."""
    print("=" * 80)
    print("VALIDACION LEGACY_UNIVARIADOS (solo lectura)")
    print("=" * 80)

    if not validacion.ok:
        print("NO SE PUEDE INTEGRAR -- problemas bloqueantes:")
        for p in validacion.problemas:
            print(f"  - {p}")
        return

    print(f"metricas_global.csv: {validacion.n_filas_metricas:,} filas, columnas: {validacion.columnas_metricas}")
    print(f"series_global.csv:   {validacion.n_filas_series:,} filas, columnas: {validacion.columnas_series}")

    print(f"\nRegiones en metricas_global.csv ({len(validacion.regiones_metricas)}): {validacion.regiones_metricas}")
    print(f"Regiones en series_global.csv   ({len(validacion.regiones_series)}): {validacion.regiones_series}")

    print(f"\nEstrategias en metricas_global.csv ({len(validacion.estrategias_metricas)}): {validacion.estrategias_metricas}")
    print(f"Estrategias 'prediccion' en series_global.csv ({len(validacion.estrategias_series_prediccion)}): {validacion.estrategias_series_prediccion}")

    print(f"\nTipos de serie encontrados: {validacion.tipos_series}")
    print(f"  Existe 'real': {validacion.tiene_real}")
    print(f"  Existe 'componente_pred': {validacion.tiene_componente_pred}")

    print("\nN predicciones por (region, estrategia):")
    for (region, estrategia), n in sorted(validacion.n_predicciones_por_region_estrategia.items()):
        print(f"  {region:6s} | {estrategia:45s} | {n}")

    print("\nVentana de prediccion por estrategia (min/max de 'fecha' en filas tipo=prediccion):")
    for estrategia, (min_ts, max_ts) in sorted(validacion.ventana_prediccion_por_estrategia.items()):
        print(f"  {estrategia:45s} | {min_ts} .. {max_ts}")

    if validacion.estrategias_sin_mapeo:
        print(f"\nAVISO: estrategias SIN mapeo a modelo canonico: {validacion.estrategias_sin_mapeo}")

    if validacion.problemas:
        print("\nProblemas/avisos encontrados:")
        for p in validacion.problemas:
            print(f"  - {p}")
    else:
        print("\nSin problemas encontrados.")


@dataclass
class LegacyUnivariadoResultado:
    metricas_df: pd.DataFrame
    pred_df: pd.DataFrame
    real_df: pd.DataFrame
    entradas_reporte: list
    validacion: ValidacionLegacyUnivariado
    estrategias_sin_mapeo: list


def procesar_legacy_univariado(
    legacy_metricas_df: pd.DataFrame,
    legacy_series_df: pd.DataFrame,
    legacy_metricas_path: str,
    legacy_series_path: str,
    verbose: bool = True,
) -> LegacyUnivariadoResultado:
    """
    Transforma los 2 CSV legacy YA LEIDOS (nunca se modifican) al mismo
    esquema que usan metricas_master/series_master:

      - `familia_experimento` se fija DIRECTO a "univariado"
        (FAMILIA_UNIVARIADO) -- NUNCA pasa por clasificar_familia(), que es
        exclusiva de corridas modernas con config.json (modelo+exogenas).
      - `modelo` (canonico) sale de MAPEO_ESTRATEGIA_LEGACY_UNIVARIADO; una
        estrategia SIN mapeo se incluye igual (nunca se pierden resultados
        reales por esto) con modelo=None y un AVISO explicito -- nunca se
        inventa un id canonico.
      - `run_name` sale de build_run_name_legacy_univariado(estrategia).
      - `forecast_horizon` se confirma con series_global.csv: si TODAS las
        regiones de una estrategia coinciden en el mismo numero de
        predicciones, ese numero se usa; si no coinciden (o no hay
        predicciones para esa estrategia), queda None -- nunca se asume
        168 sin confirmarlo.
      - `train_hours`/`optuna_n_trials`/`seed`/`git_commit`/`generated_at`
        quedan en None (sin evidencia en los CSV legacy para derivarlos).
      - `exogenas`/`exogena_individual`: vacio/None (univariado, sin
        exogenas por definicion).
      - `run_dir` apunta a la ruta legacy original (metricas o series,
        segun corresponda).

    Lanza `ValueError` si `validar_legacy_univariado()` encuentra columnas
    requeridas ausentes (no se integra a medias).
    """
    validacion = validar_legacy_univariado(legacy_metricas_df, legacy_series_df)

    if not validacion.ok:
        raise ValueError(
            "Los CSV legacy no tienen el esquema minimo requerido -- no se integra a medias. "
            f"Problemas: {validacion.problemas}"
        )

    if verbose:
        imprimir_validacion_legacy(validacion)

    # ---------------------------------------------------------------
    # forecast_horizon confirmado por estrategia (ver docstring)
    # ---------------------------------------------------------------
    conteos_por_estrategia = {}
    for (region, estrategia), n in validacion.n_predicciones_por_region_estrategia.items():
        conteos_por_estrategia.setdefault(estrategia, set()).add(n)

    horizonte_por_estrategia = {}
    for estrategia, valores in conteos_por_estrategia.items():
        if len(valores) == 1:
            horizonte_por_estrategia[estrategia] = next(iter(valores))
        elif verbose:
            print(
                f"AVISO: '{estrategia}' tiene distinto numero de predicciones segun la region "
                "-- forecast_horizon queda sin confirmar (None)."
            )

    estrategias_presentes = sorted(set(validacion.estrategias_metricas) | set(validacion.estrategias_series_prediccion))

    filas_metadata = []
    for estrategia in estrategias_presentes:
        filas_metadata.append({
            "modelo_estrategia": estrategia,
            "run_name": build_run_name_legacy_univariado(estrategia),
            "modelo": MAPEO_ESTRATEGIA_LEGACY_UNIVARIADO.get(estrategia),
            "familia_experimento": FAMILIA_UNIVARIADO,
            "exogenas": "",
            "exogena_individual": None,
            "train_hours": None,
            "forecast_horizon": horizonte_por_estrategia.get(estrategia),
            "optuna_n_trials": None,
            "seed": None,
            "notas": "Importado de Legacy_Univariados -- NO es una corrida moderna (sin config.json, sin runner.py).",
            "git_commit": None,
            "generated_at": None,
        })
    metadata_df = pd.DataFrame(filas_metadata)

    # ---------------------------------------------------------------
    # metricas_global.csv -> filas listas para pd.concat con metricas_master
    # ---------------------------------------------------------------
    metricas_legacy = legacy_metricas_df.copy()
    metricas_legacy["region"] = _resolver_columna_region(metricas_legacy)
    metricas_legacy = _renombrar_modelo_original(metricas_legacy)
    metricas_legacy = _evitar_colision_metadata(metricas_legacy)
    metricas_legacy = metricas_legacy.merge(metadata_df, on="modelo_estrategia", how="left")
    metricas_legacy["run_dir"] = legacy_metricas_path

    # ---------------------------------------------------------------
    # series_global.csv -> prediccion (extra_pred_frames) + real (extra_real_frames)
    # componente_pred (y cualquier otro tipo que no sea real/prediccion) se
    # excluye aca, igual que en construir_series_master() para corridas
    # modernas.
    # ---------------------------------------------------------------
    series_legacy = legacy_series_df.copy()
    series_legacy["region"] = _resolver_columna_region(series_legacy)
    series_legacy["fecha"] = pd.to_datetime(series_legacy["fecha"], errors="coerce")
    series_legacy = _renombrar_modelo_original(series_legacy)
    series_legacy = series_legacy.rename(columns={"fecha": "timestamp", "tipo": "serie_tipo"})

    pred_legacy = series_legacy[series_legacy["serie_tipo"] == "prediccion"].copy()
    real_legacy = series_legacy[series_legacy["serie_tipo"] == "real"].copy()

    pred_legacy = _evitar_colision_metadata(pred_legacy)
    pred_legacy = pred_legacy.merge(metadata_df, on="modelo_estrategia", how="left")
    pred_legacy["run_dir"] = legacy_series_path

    real_legacy = real_legacy[["region", "timestamp", "valor", "modelo_estrategia"]].copy()

    # ---------------------------------------------------------------
    # reporte_consolidacion: una fila por estrategia legacy
    # ---------------------------------------------------------------
    entradas_reporte = []
    for _, fila in metadata_df.iterrows():
        razon = (
            "" if fila["modelo"] is not None
            else f"estrategia legacy sin mapeo en MAPEO_ESTRATEGIA_LEGACY_UNIVARIADO -- modelo=None"
        )
        entradas_reporte.append({
            "run_name": fila["run_name"],
            "familia": FAMILIA_UNIVARIADO,
            "estado": "completo",
            "incluido": True,
            "razon": razon,
        })

    return LegacyUnivariadoResultado(
        metricas_df=metricas_legacy,
        pred_df=pred_legacy,
        real_df=real_legacy,
        entradas_reporte=entradas_reporte,
        validacion=validacion,
        estrategias_sin_mapeo=validacion.estrategias_sin_mapeo,
    )


# =========================================================
# API DE ALTO NIVEL
# =========================================================

def consolidar_resultados(
    pipeline_resultados_dir: str,
    output_dir: Optional[str] = None,
    regiones_esperadas: Optional[list] = None,
    escribir_csv: bool = True,
    escribir_reporte: bool = True,
    legacy_metricas_path: Optional[str] = None,
    legacy_series_path: Optional[str] = None,
):
    """
    Punto de entrada unico: descubre las corridas MODERNAS completas, arma
    `metricas_master.csv`/`series_master.csv`/`reporte_consolidacion.csv`,
    y (si `escribir_csv=True`, default) los escribe en `output_dir` --
    por defecto, `pipeline_resultados_dir/Consolidado/` (subcarpeta
    dedicada, nunca mezclada con las carpetas de corridas: el propio
    `descubrir_runs_completos()` la excluye del descubrimiento). Solo
    lectura sobre las carpetas de corridas existentes; nunca las modifica
    ni las borra.

    `legacy_metricas_path`/`legacy_series_path` (opcionales, default
    `None` -> comportamiento IDENTICO al de antes, solo corridas modernas):
    si se pasan AMBOS, se leen esos 2 CSV (nunca se modifican/mueven/
    sobreescriben) y se integran como quinta familia experimental
    `familia_experimento="univariado"` -- ver `procesar_legacy_univariado()`
    para el detalle exacto de mapeo/metadata. Si se pasa SOLO UNO de los
    dos, se lanza `ValueError` de inmediato: nunca se integra a medias en
    silencio.

    Idempotente: cada llamada reconstruye todo desde `Pipeline_Resultados/`
    (y, si se pidio, desde los 2 CSV legacy) -- nunca lee su propia salida
    anterior, asi que correrlo varias veces seguidas sobre los mismos
    resultados produce el mismo contenido, sin acumular ni duplicar nada.

    Devuelve `(metricas_df, series_df, descubrimiento)`.
    """
    if bool(legacy_metricas_path) != bool(legacy_series_path):
        raise ValueError(
            "Se paso solo uno de legacy_metricas_path/legacy_series_path -- se requieren "
            "AMBOS para integrar Legacy_Univariados (o ninguno de los dos para omitirlo). "
            f"legacy_metricas_path={legacy_metricas_path!r}, legacy_series_path={legacy_series_path!r}"
        )

    integrar_legacy = bool(legacy_metricas_path and legacy_series_path)

    if integrar_legacy:
        if not os.path.exists(legacy_metricas_path):
            raise FileNotFoundError(f"legacy_metricas_path no existe: {legacy_metricas_path}")
        if not os.path.exists(legacy_series_path):
            raise FileNotFoundError(f"legacy_series_path no existe: {legacy_series_path}")

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

    metricas_df = construir_metricas_master(descubrimiento.runs)

    legacy_resultado = None
    extra_pred_frames = None
    extra_real_frames = None

    if integrar_legacy:
        print("\n" + "=" * 80)
        print("INTEGRANDO LEGACY_UNIVARIADOS")
        print("=" * 80)
        print(f"Metricas: {legacy_metricas_path}")
        print(f"Series:   {legacy_series_path}")

        legacy_metricas_df = pd.read_csv(legacy_metricas_path, encoding="utf-8-sig")
        legacy_series_df = pd.read_csv(legacy_series_path, encoding="utf-8-sig")

        legacy_resultado = procesar_legacy_univariado(
            legacy_metricas_df, legacy_series_df, legacy_metricas_path, legacy_series_path, verbose=True,
        )

        metricas_df = pd.concat([metricas_df, legacy_resultado.metricas_df], ignore_index=True, sort=False)
        extra_pred_frames = [legacy_resultado.pred_df]
        extra_real_frames = [legacy_resultado.real_df]

    # UNA sola construccion de series_master (moderno, mas legacy si se
    # paso) -- evita releer series.csv de cada corrida dos veces.
    series_df = construir_series_master(
        descubrimiento.runs, verbose=True,
        extra_pred_frames=extra_pred_frames, extra_real_frames=extra_real_frames,
    )

    ventanas_por_run = calcular_ventanas_agregadas_por_run(series_df)
    metricas_df = agregar_ventanas_temporales(metricas_df, series_df)

    reporte_df = construir_reporte_consolidacion(
        descubrimiento,
        ventanas_por_run=ventanas_por_run,
        entradas_legacy=legacy_resultado.entradas_reporte if legacy_resultado else None,
    )

    if descubrimiento.runs or legacy_resultado:
        por_familia = pd.Series(
            [r.familia_experimento for r in descubrimiento.runs]
            + ([FAMILIA_UNIVARIADO] * len(legacy_resultado.entradas_reporte) if legacy_resultado else [])
        ).value_counts()
        print("\nCorridas completas por familia (moderno + legacy):")
        for familia, n in por_familia.items():
            print(f"  {familia}: {n}")

        por_modelo = pd.Series(
            [r.modelo for r in descubrimiento.runs]
            + (legacy_resultado.metricas_df.drop_duplicates("run_name")["modelo"].tolist() if legacy_resultado else [])
        ).value_counts(dropna=False)
        print("\nCorridas completas por modelo (moderno + legacy):")
        for modelo, n in por_modelo.items():
            print(f"  {modelo}: {n}")

    if legacy_resultado:
        print(f"\nRuns modernos incluidos: {len(descubrimiento.runs)}")
        print(f"Runs legacy incluidos:   {len(legacy_resultado.entradas_reporte)}")
        if legacy_resultado.estrategias_sin_mapeo:
            print(f"AVISO: {len(legacy_resultado.estrategias_sin_mapeo)} estrategia(s) legacy sin mapeo canonico: {legacy_resultado.estrategias_sin_mapeo}")

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
