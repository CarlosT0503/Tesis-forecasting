"""
Piloto H24, alternativa E (aislado: NO modifica codigo, configuraciones ni resultados existentes).

Procedimiento E, con 504 h historicas antes de la prueba:
  - horas 1-336   -> entrenamiento de Optuna,
  - horas 337-504 -> validacion (168 h),
  - se eligen los hiperparametros con la validacion,
  - se reentrena con las 336 h inmediatamente anteriores a la prueba (las ultimas 336 de las 504),
  - pronostico recursivo de las 168 h de prueba.

Reutiliza SIN cambios `xgboost_model._preparar_serie` (llamado con train_hours=504), `objective_xgboost`
y `forecast_xgboost_tuned`. Escribe solo en resultados_locales/H24_piloto_E/ (ignorada por git).

    python scripts/piloto_h24_xgboost_e.py --region CEN --exog Generacion --trials 80
"""
import argparse
import ast
import json
import os
import sys
import time
import warnings

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"
warnings.filterwarnings("ignore")

import numpy as np  # noqa: E402
import optuna  # noqa: E402
import pandas as pd  # noqa: E402
from optuna.samplers import TPESampler  # noqa: E402
from optuna.trial import FixedTrial  # noqa: E402

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(RAIZ, "src"))
from tesis_forecast.data.exogenas import cargar_exogenas_horarias  # noqa: E402
from tesis_forecast.metrics import calcular_metricas  # noqa: E402
from tesis_forecast.models import xgboost_model as X  # noqa: E402

optuna.logging.set_verbosity(optuna.logging.WARNING)
ap = argparse.ArgumentParser()
ap.add_argument("--region", default="CEN")
ap.add_argument("--exog", nargs="+", default=["Generacion"])
ap.add_argument("--trials", type=int, default=80)
ap.add_argument("--data-dir", default=os.path.join(RAIZ, "datos_locales"))
ap.add_argument("--salida", default=os.path.join(RAIZ, "resultados_locales", "H24_piloto_E"))
args = ap.parse_args()
os.makedirs(args.salida, exist_ok=True)
H, W = 168, 168  # horizonte y ventana de lags (sin cambios)
REG, EXOG = args.region, list(args.exog)
NOMBRE = REG + "_DEMANDA"
informe = {"region": REG, "exogenas": EXOG, "trials": args.trials}


def preparar(train_hours, exog_cols, exogenas_df, serie, fechas):
    return X._preparar_serie(NOMBRE, serie, fechas, exogenas_df, exog_cols, train_hours, H)


def cargar(exog_cols):
    df = X.cargar_regiones([REG], args.data_dir)[REG]
    serie, fechas = X.extraer_serie_horaria(df, X.COL_DEMANDA, NOMBRE)
    glob = cargar_exogenas_horarias(data_dir=args.data_dir)
    return serie, fechas, X.merge_exogenas(REG, glob, exog_cols, args.data_dir)


t_total = time.time()
serie, fechas, exogenas_df = cargar(EXOG)
ctx = preparar(504, EXOG, exogenas_df, serie, fechas)  # contexto E
ctx_old = preparar(336, EXOG, exogenas_df, serie, fechas)  # contexto de la configuracion anterior
print("\n=== A. Estructura temporal de E ===")
n_tr, n_va = len(ctx["tune_train_y"]), len(ctx["tune_val_y"])
fi = fechas[len(serie) - 504 - H:]
print(f"tune_train: {n_tr} h | validacion: {n_va} h | prueba: {len(ctx['test'])} h")
print("Fechas: entrenamiento Optuna", fi[0], "->", fi[n_tr - 1], "| validacion", fi[n_tr], "->", fi[n_tr + n_va - 1],
      "| reentrenamiento final", fi[168], "->", fi[503], "| prueba", fi[504], "->", fi[-1])
train_f = ctx["train"][-336:]
train_exog_f = ctx["train_exog"].iloc[-336:].reset_index(drop=True)
assert np.array_equal(train_f, ctx_old["train"]), "el reentrenamiento final no coincide con las 336 h previas a la prueba"
assert np.array_equal(ctx["test"], ctx_old["test"])
assert np.allclose(train_exog_f.values, ctx_old["train_exog"].values)
assert np.allclose(ctx["test_exog"].values, ctx_old["test_exog"].values)
print("OK: las 336 h de reentrenamiento y la prueba son IDENTICAS a las de la configuracion anterior.")
filas_tuning = len(X.create_feature_df(ctx["tune_train_y"], W, EXOG, ctx["train_exog_tune"]))
filas_val = len(X.create_feature_df(np.concatenate([ctx["tune_train_y"], ctx["tune_val_y"]]), W, EXOG,
                                    pd.concat([ctx["train_exog_tune"], ctx["val_exog_tune"]], ignore_index=True)))
print(f"filas utilizables en tuning: {filas_tuning} (minimo 50) | filas de contexto de validacion: {filas_val} (necesita >= {n_va})")
informe.update(filas_tuning=filas_tuning, filas_contexto_validacion=filas_val)

print("\n=== B. Pruebas de ausencia de informacion futura ===")
rng = np.random.default_rng(0)
# B1. causalidad de las variables derivadas de la demanda: alterar y[t:] no cambia la fila t
y = np.concatenate([ctx["tune_train_y"], ctx["tune_val_y"]])
ex = pd.concat([ctx["train_exog_tune"], ctx["val_exog_tune"]], ignore_index=True)
base = X.create_feature_df(y, W, EXOG, ex)
ok = True
for t in (336, 340, 420, 503):
    y2 = y.copy()
    y2[t:] = rng.uniform(0.2, 5, size=len(y) - t) * y.mean()
    f2 = X.create_feature_df(y2, W, EXOG, ex)
    cols = [c for c in base.columns if c != "y"]
    ok &= bool(np.allclose(base.loc[t, cols].values.astype(float), f2.loc[t, cols].values.astype(float)))
print("B1 fila de validacion t no cambia al alterar la demanda en t..fin:", ok)
informe["B1_causalidad_demanda"] = ok
# B2. la prueba no influye en nada de lo que usa Optuna: alterar demanda y exogenas de la semana de prueba
serie2 = serie.copy()
serie2[-H:] = rng.uniform(0.2, 5, size=H) * serie.mean()
exog2 = exogenas_df.copy()
exog2.loc[exog2["datetime"] >= pd.Timestamp(fechas[len(serie) - H]), EXOG] *= 7.0
ctx2 = preparar(504, EXOG, exog2, serie2, fechas)
ok2 = all(np.array_equal(np.asarray(ctx[k]), np.asarray(ctx2[k])) for k in ("tune_train_y", "tune_val_y")) and \
    all(np.allclose(ctx[k].values, ctx2[k].values) for k in ("train_exog_tune", "val_exog_tune"))
print("B2 los datos de tuning/validacion no cambian al alterar la semana de prueba:", ok2)
informe["B2_prueba_no_influye"] = bool(ok2)
# B3. las exogenas estimadas de validacion solo usan datos anteriores al inicio de la validacion
exo_ctx = exogenas_df.copy()
a = X.alinear_exogenas_a_fechas(fechas, exo_ctx, EXOG)
inicio = len(serie) - 504 - H
ctx_x = a.iloc[max(0, inicio - 336):].reset_index(drop=True)
off = inicio - max(0, inicio - 336)
val_start = off + n_tr
v1 = X.construir_future_exog(ctx_x, val_start, n_va, EXOG)
ctx_y = ctx_x.copy()
ctx_y.loc[val_start:, EXOG] = ctx_y.loc[val_start:, EXOG] * 9.0 + 1.0
v2 = X.construir_future_exog(ctx_y, val_start, n_va, EXOG)
solo_lag = [c for c in EXOG if c in X.EXOG_NO_CONOCIDAS_FUTURO]
ok3 = all(np.allclose(v1[c].values, v2[c].values) for c in solo_lag) if solo_lag else True
print("B3 exogenas operativas de validacion (promedio t-168/t-336) no dependen de datos desde el inicio de la validacion:", ok3,
      "| variables operativas:", solo_lag)
print("   Temperatura/IGAE (si estan activas) se usan con su valor del periodo, igual que en el diseno original.")
informe["B3_exogenas_validacion"] = ok3
informe["orden_temporal"] = "tune_train < validacion < reentrenamiento final (incluye la validacion) < prueba"

print("\n=== C. Optuna: %d intentos reales (los 10 primeros = presupuesto de una region en el diseno actual) ===" % args.trials)
tiempos = []


def objetivo(trial):
    s = time.time()
    v = X.objective_xgboost(trial, ctx["tune_train_y"], ctx["tune_val_y"], W, EXOG, ctx["train_exog_tune"], ctx["val_exog_tune"])
    tiempos.append(time.time() - s)
    return v


estudio = optuna.create_study(direction="minimize", sampler=TPESampler(seed=42))
t0 = time.time()
estudio.optimize(objetivo, n_trials=args.trials, show_progress_bar=False)
t_opt = time.time() - t0
vals = np.array([t.value for t in estudio.trials], dtype=float)
fin = np.isfinite(vals)
print(f"intentos finitos: {int(fin.sum())}/{len(vals)} | tiempo Optuna: {t_opt:.0f} s | por intento: media {np.mean(tiempos):.1f} s")


def mejor(n):
    i = int(np.nanargmin(np.where(np.isfinite(vals[:n]), vals[:n], np.nan)))
    return i, float(vals[i]), dict(estudio.trials[i].params)


pd.DataFrame({"intento": range(len(vals)), "sMAPE_validacion": vals, "segundos": tiempos}).to_csv(
    os.path.join(args.salida, f"trials_{REG}_{'-'.join(EXOG)}.csv"), index=False)

print("\n=== D. Metricas: VALIDACION y PRUEBA por separado (la prueba NO se uso para elegir nada) ===")
old_dir = os.path.join(RAIZ, "resultados_locales", "Pipeline_Resultados_Ventanas", "S4", "XGBoost_train336h_fh168h_" + "-".join(
    {"Temperatura": "Temp", "IGAE": "IGAE", "Generacion": "Gen", "Importacion": "Imp", "Exportacion": "Exp"}[e] for e in EXOG))
cu = pd.read_csv(os.path.join(old_dir, "config_usada.csv"))
p_old = ast.literal_eval(cu[cu["region"] == REG].parametros.iloc[0])
m_old = pd.read_csv(os.path.join(old_dir, "metricas.csv"))
m_old = m_old[m_old["region"] == REG].iloc[0]
cand = {"anterior (intento 0, sin tuning)": ("-", float("nan"), p_old)}
for n in (10, args.trials):
    if n <= len(vals):
        cand[f"E, mejor de los primeros {n} intentos"] = (mejor(n)[0], mejor(n)[1], mejor(n)[2])
filas = []
for nombre, (idx, _, params) in cand.items():
    v_val = X.objective_xgboost(FixedTrial(params), ctx["tune_train_y"], ctx["tune_val_y"], W, EXOG, ctx["train_exog_tune"], ctx["val_exog_tune"])
    pred = X.forecast_xgboost_tuned(train_f, H, params, W, EXOG, train_exog_f, ctx["test_exog"])
    met = calcular_metricas(ctx["test"], pred)
    filas.append({"configuracion": nombre, "intento": idx, "sMAPE_validacion": round(v_val, 4),
                  "MAPE_prueba": round(met["MAPE"], 4), "sMAPE_prueba": round(met["sMAPE"], 4),
                  "MAE_prueba": round(met["MAE"], 2), "RMSE_prueba": round(met["RMSE"], 2), "parametros": params})
res = pd.DataFrame(filas)
print(res.drop(columns="parametros").to_string(index=False))
print("\nParametros:")
for f in filas:
    print(" -", f["configuracion"], f["parametros"])
print(f"\nCOMPROBACION: MAPE de prueba con los parametros anteriores recalculado aqui = {filas[0]['MAPE_prueba']:.4f} | guardado en la corrida S4 = {m_old['MAPE']:.4f}")
informe["reproduce_corrida_anterior"] = bool(abs(filas[0]["MAPE_prueba"] - float(m_old["MAPE"])) < 1e-3)
informe["tabla"] = filas
res.to_csv(os.path.join(args.salida, f"comparacion_{REG}_{'-'.join(EXOG)}.csv"), index=False)

print("\n=== E. Variables 'constantes': verificacion de matrices de caracteristicas (8 regiones, S4) ===")
cols5 = ["Temperatura", "IGAE", "Importacion", "Exportacion"]
fil_c = []
glob = cargar_exogenas_horarias(data_dir=args.data_dir)
for r in ["BCA", "CEN", "NES", "NOR", "NTE", "OCC", "ORI", "PEN"]:
    dfr = X.cargar_regiones([r], args.data_dir)[r]
    s_r, f_r = X.extraer_serie_horaria(dfr, X.COL_DEMANDA, r + "_DEMANDA")
    ex_r = X.merge_exogenas(r, glob, cols5, args.data_dir)
    c_r = X._preparar_serie(r + "_DEMANDA", s_r, f_r, ex_r, cols5, 504, H)
    fila = {"region": r}
    for c in cols5:
        full = np.concatenate([c_r["train_exog"][c].values, c_r["test_exog"][c].values])
        fila[c + "_valores_distintos_en_672h"] = int(pd.Series(full).nunique())
    # matrices de caracteristicas con la demanda: identicas salvo la columna constante
    mats = {}
    for c in cols5:
        d = X.create_feature_df(c_r["train"], W, [c], c_r["train_exog"][[c]])
        mats[c] = d.drop(columns=[c]).values
    fila["matrices_identicas_sin_la_columna_exogena"] = bool(all(np.array_equal(mats[cols5[0]], mats[c]) for c in cols5[1:]))
    fil_c.append(fila)
cdf = pd.DataFrame(fil_c)
print(cdf.to_string(index=False))
informe["constantes"] = fil_c
# prediccion final identica entre configuraciones con una sola variable constante, mismos parametros (region piloto)
pe = mejor(args.trials)[2]
preds = {}
for c in cols5:
    exo = X.merge_exogenas(REG, glob, [c], args.data_dir)
    cx = X._preparar_serie(NOMBRE, serie, fechas, exo, [c], 504, H)
    tf_ = cx["train"][-336:]
    te_ = cx["train_exog"].iloc[-336:].reset_index(drop=True)
    preds[c] = X.forecast_xgboost_tuned(tf_, H, pe, W, [c], te_, cx["test_exog"])
    vv = X.objective_xgboost(FixedTrial(pe), cx["tune_train_y"], cx["tune_val_y"], W, [c], cx["train_exog_tune"], cx["val_exog_tune"])
    preds[c + "_val"] = vv
iguales = all(np.array_equal(preds[cols5[0]], preds[c]) for c in cols5[1:])
vigual = all(preds[cols5[0] + "_val"] == preds[c + "_val"] for c in cols5[1:])
print(f"Con los mismos parametros, prediccion de prueba bit a bit identica entre Temp/IGAE/Imp/Exp: {iguales} | sMAPE de validacion identico: {vigual}")
informe["constantes_predicciones_identicas"] = bool(iguales)
informe["constantes_validacion_identica"] = bool(vigual)

informe["tiempo_total_s"] = round(time.time() - t_total, 1)
informe["tiempo_optuna_s"] = round(t_opt, 1)
informe["tiempo_medio_por_intento_s"] = round(float(np.mean(tiempos)), 2)
informe["intentos_finitos"] = int(fin.sum())
with open(os.path.join(args.salida, f"informe_{REG}_{'-'.join(EXOG)}.json"), "w", encoding="utf-8") as f:
    json.dump(informe, f, indent=2, ensure_ascii=False, default=str)
print(f"\nTIEMPO TOTAL del piloto: {informe['tiempo_total_s']} s | solo Optuna ({args.trials} intentos): {informe['tiempo_optuna_s']} s")
print("FIN")
