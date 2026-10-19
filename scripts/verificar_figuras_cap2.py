"""
Recalcula, desde los archivos fuente, las cifras que respaldan las Figuras 2.1-2.5 del Capitulo 2 y el
contexto regional de R16. Solo lectura. Uso:

    python scripts/verificar_figuras_cap2.py <carpeta_SIE> <carpeta_long_csv> <carpeta_salida>

<carpeta_SIE>   contiene "Consumo de energia electrica por entidad federativa.csv" y
                "Generación bruta de energía eléctrica por entidad federativa.csv" (Sistema de Informacion Energetica).
<carpeta_long_csv> contiene {REGION}_long.csv (series procesadas de CENACE).
Escribe CSV con: consumo anual nacional, generacion anual nacional, generacion vs consumo por estado,
patrones de demanda 2023 por region y balance regional 2023.
"""
import csv
import os
import sys

import pandas as pd

SIE, LONG, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(OUT, exist_ok=True)
DEM = "Estimacion de Demanda por Balance (MWh)"
REG = ["BCA", "CEN", "NES", "NOR", "NTE", "OCC", "ORI", "PEN"]

# --- consumo anual por entidad (GWh) ---
raw = pd.read_csv(os.path.join(SIE, "Consumo de energia electrica por entidad federativa.csv"), skiprows=8, index_col=0)
raw.index = raw.index.astype(str).str.strip()
raw = raw[[c for c in raw.columns if str(c).strip().isdigit()]]
raw.columns = [int(str(c).strip()) for c in raw.columns]
raw = raw.apply(pd.to_numeric, errors="coerce").dropna(how="all")
total = raw.loc[[i for i in raw.index if i.lower().startswith("total")][0]]
cons = raw.drop([i for i in raw.index if i.lower().startswith("total")])
total.rename("consumo_total_GWh").to_csv(os.path.join(OUT, "consumo_anual_nacional.csv"), header=True)

# --- generacion mensual por entidad (MWh) ---
rows = list(csv.reader(open(os.path.join(SIE, "Generación bruta de energía eléctrica por entidad federativa.csv"), encoding="utf-8-sig")))
h = next(i for i, r in enumerate(rows) if len(r) > 2 and r[1].strip().startswith("ENE/2002"))
cols = [x.strip() for x in rows[h][1:] if x.strip()]
body = [r for r in rows[h + 1:] if r and r[0].strip() and len(r) > len(cols)]
gen = pd.DataFrame([[r[0].strip()] + r[1:len(cols) + 1] for r in body], columns=["estado"] + cols).set_index("estado")
gen = gen.apply(lambda s: pd.to_numeric(s.astype(str).str.replace(",", "").str.strip(), errors="coerce")).dropna(how="all")
tot = gen.loc["Total"]
gen_anual = pd.Series({y: tot[[c for c in gen.columns if c.endswith("/%d" % y)]].sum() for y in range(2002, 2025)}, name="generacion_total_MWh")
meses2024 = len([c for c in gen.columns if c.endswith("/2024")])
gen_anual.to_csv(os.path.join(OUT, "generacion_anual_nacional.csv"), header=True)

# --- generacion vs consumo por estado (media 2006-2023, GWh/ano) ---
est = gen.drop(["Total"] + [i for i in gen.index if i.startswith("Plantas")])
anual_est = pd.DataFrame({y: est[[c for c in gen.columns if c.endswith("/%d" % y)]].sum(axis=1) / 1e3 for y in range(2006, 2024)})
cmp = pd.DataFrame({"generacion_GWh": anual_est.mean(axis=1), "consumo_GWh": cons.loc[:, 2006:2023].mean(axis=1).reindex(anual_est.index)})
cmp["generacion_entre_consumo"] = cmp.generacion_GWh / cmp.consumo_GWh
cmp.sort_values("generacion_entre_consumo", ascending=False).round(3).to_csv(os.path.join(OUT, "generacion_vs_consumo_por_estado.csv"))

# --- patrones de demanda 2023 por region y balance regional 2023 ---
pat, bal = {}, []
for r in REG:
    d = pd.read_csv(os.path.join(LONG, "%s_long.csv" % r))
    d.columns = [c.strip() for c in d.columns]
    d["f"] = pd.to_datetime(d["fecha"])
    x = d[d.f.dt.year == 2023].copy()
    x["h"] = pd.to_numeric(x["Hora"])
    mm = x.groupby(x.f.dt.month)[DEM].mean()
    dia = x.groupby("f")[DEM].mean()
    dd = dia.groupby(dia.index.dayofweek).mean()
    perf = x[x.h <= 24].groupby("h")[DEM].mean()
    pat[r] = dict(media_MWh_h=x[DEM].mean(), mes_pico=int(mm.idxmax()), mes_valle=int(mm.idxmin()), max_entre_min_mensual=mm.max() / mm.min(),
                  domingo_entre_laborable=dd[6] / dd[:5].mean(), hora_pico_reporte=int(perf.idxmax()), hora_valle_reporte=int(perf.idxmin()))
    g, i, e, dem = (x["Generacion (MWh)"].sum() / 1e6, x["Importacion Total (MWh)"].sum() / 1e6, x["Exportacion Total (MWh)"].sum() / 1e6, x[DEM].sum() / 1e6)
    bal.append(dict(region=r, generacion_TWh=g, importacion_TWh=i, exportacion_TWh=e, demanda_TWh=dem, intercambio_neto_TWh=dem - (g + i - e)))
pd.DataFrame(pat).T.round(4).to_csv(os.path.join(OUT, "patrones_demanda_2023.csv"))
pd.DataFrame(bal).set_index("region").round(4).to_csv(os.path.join(OUT, "balance_regional_2023.csv"))
print("meses de 2024 en la generacion:", meses2024, "| consumo 2024 / 2023: %.1f%%" % (100 * total[2024] / total[2023]))
print("escrito en", OUT)
