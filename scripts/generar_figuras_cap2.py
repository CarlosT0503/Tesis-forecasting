"""
Regenera las Figuras 2.1, 2.2, 2.4 y 2.5 del Capitulo 2 desde los CSV del SIE (solo lectura sobre los datos;
NO sobrescribe las imagenes originales de la tesis). Uso:

    python scripts/generar_figuras_cap2.py <carpeta_SIE> <carpeta_salida>

Decisiones de comparabilidad (ver docs/correcciones_tesis/R16_contexto_sistema_electrico.md):
  - Fig 2.2: 2024 se conserva pero se dibuja como periodo PARCIAL (enero-junio), con marcador, linea y nota distintos.
  - Fig 2.5: ventas de CFE Suministro Basico (serie "consumo" del SIE) y generacion en GWh/ano, promedio 2006-2023 (anos completos en ambas tablas).
    Morelos queda fuera de la comparacion (la generacion tiene datos solo desde mar-2017 y 47 meses en cero);
    Aguascalientes, Tabasco, Tlaxcala y Zacatecas no tienen fila de generacion en la fuente (solo se muestran sus ventas).
  - Fig 2.1: mismo calculo que la original (promedio anual 2006-2024), con el periodo real y la advertencia de 2024 parcial.
    Incluir 2024 (solo enero-junio) reduce cada promedio entre 1.6 % y 3.2 % respecto de 2006-2023 y solo intercambia
    dos pares de entidades de valores casi iguales (Baja California/Sonora y Chiapas/Guerrero).
  - Fig 2.4: generacion anual promedio 2002-2024 en GWh/ano (la original era mensual en MWh), Morelos con marca de cobertura parcial.
"""
import csv
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib import cm  # noqa: E402

SIE, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
BG, FG, GRID = "#0b0b0b", "white", "#2a7f86"
plt.rcParams.update({"figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG, "text.color": FG,
                     "axes.labelcolor": FG, "xtick.color": FG, "ytick.color": FG, "axes.edgecolor": "#555555",
                     "font.size": 10})
FUENTE = "Fuente: Sistema de Información Energética (SIE), Secretaría de Energía."
NOTA_SIE = "Serie del SIE rotulada \"consumo\"; coincide con las ventas de CFE Suministro Básico de SENER en 2019–2023 (identificación inferida; años previos, no verificados)."


def miles(x, _=None):
    return f"{x:,.0f}".replace(",", " ")


# ---------- datos ----------
raw = pd.read_csv(os.path.join(SIE, "Consumo de energia electrica por entidad federativa.csv"), skiprows=8, index_col=0)
raw.index = raw.index.astype(str).str.strip()
raw = raw[[c for c in raw.columns if str(c).strip().isdigit()]]
raw.columns = [int(str(c).strip()) for c in raw.columns]
raw = raw.apply(pd.to_numeric, errors="coerce").dropna(how="all")
total = raw.loc[[i for i in raw.index if i.lower().startswith("total")][0]]
cons = raw.drop([i for i in raw.index if i.lower().startswith("total")])

rows = list(csv.reader(open(os.path.join(SIE, "Generación bruta de energía eléctrica por entidad federativa.csv"), encoding="utf-8-sig")))
h = next(i for i, r in enumerate(rows) if len(r) > 2 and r[1].strip().startswith("ENE/2002"))
cols = [x.strip() for x in rows[h][1:] if x.strip()]
body = [r for r in rows[h + 1:] if r and r[0].strip() and len(r) > len(cols)]
gen = pd.DataFrame([[r[0].strip()] + r[1:len(cols) + 1] for r in body], columns=["estado"] + cols).set_index("estado")
gen = gen.apply(lambda s: pd.to_numeric(s.astype(str).str.replace(",", "").str.strip(), errors="coerce")).dropna(how="all")
gen_est = gen.drop(["Total"] + [i for i in gen.index if i.startswith("Plantas")])


def anual(df, y0, y1):
    """Suma anual (MWh) de la generacion; NaN si algun mes del ano falta."""
    out = {}
    for y in range(y0, y1 + 1):
        c = [x for x in df.columns if x.endswith("/%d" % y)]
        out[y] = df[c].sum(axis=1, min_count=len(c))
    return pd.DataFrame(out)


# ---------- Figura 2.2 ----------
fig, ax = plt.subplots(figsize=(10, 4.6))
anios = [a for a in total.index if a <= 2023]
ax.plot(anios, total.loc[anios], color="#39ff14", lw=2.5, marker="o", ms=6, mfc="white", mec="#39ff14", label="Años completos (enero–diciembre)")
ax.plot([2023, 2024], [total[2023], total[2024]], color="#ff9f1c", lw=1.8, ls=(0, (4, 3)))
ax.plot([2024], [total[2024]], marker="D", ms=9, mfc="none", mec="#ff9f1c", mew=2, ls="none", label="2024: solo enero–junio (parcial)")
ax.annotate("2024: enero–junio\n%s GWh\n(no comparable con años completos)" % miles(total[2024]), xy=(2024, total[2024]), xytext=(2017.2, 118000),
            color="#ff9f1c", fontsize=9.5, arrowprops=dict(arrowstyle="->", color="#ff9f1c"))
ax.set_ylim(80000, 240000)
ax.set_xlim(2005, 2025)
ax.set_xticks(range(2006, 2025, 2))
ax.yaxis.set_major_formatter(plt.FuncFormatter(miles))
ax.set_xlabel("Año")
ax.set_ylabel("Ventas de electricidad (GWh)")
ax.grid(color=GRID, lw=0.6, alpha=0.7)
ax.set_title("Ventas de electricidad de CFE Suministro Básico, total nacional, 2006–2024", fontsize=14, pad=12)
ax.legend(loc="lower left", facecolor=BG, edgecolor="#555555", labelcolor=FG, fontsize=9)
fig.text(0.01, 0.01, FUENTE + " Las cifras de 2024 son al mes de junio y no representan una caída anual." + "\n" + NOTA_SIE, fontsize=7.5, color="#bbbbbb")
fig.tight_layout(rect=(0, 0.07, 1, 1))
fig.savefig(os.path.join(OUT, "Fig2_2_Ventas_CFE_SSB_nacional.png"), dpi=200)
plt.close(fig)

# ---------- Figura 2.1 ----------
m = cons.mean(axis=1).sort_values()
fig, ax = plt.subplots(figsize=(10, 9))
colors = cm.Oranges(np.linspace(0.25, 0.95, len(m)))
ax.barh(m.index, m.values, color=colors, edgecolor="black", lw=1)
ax.xaxis.set_major_formatter(plt.FuncFormatter(miles))
ax.set_xlabel("Ventas anuales promedio (GWh/año)")
ax.set_title("Ventas anuales promedio de electricidad de CFE Suministro Básico" + "\n" + "por entidad federativa, 2006–2024", fontsize=14, pad=12)
ax.grid(axis="x", color=GRID, lw=0.5, alpha=0.5)
fig.text(0.01, 0.01, FUENTE + "\nPromedio de 2006–2024; 2024 incluye solo enero–junio, lo que reduce cada promedio entre 1.6 % y 3.2 % respecto de 2006–2023"
         + "\n(solo se intercambian dos pares de entidades de valores casi iguales: Baja California/Sonora y Chiapas/Guerrero)." + "\n" + NOTA_SIE, fontsize=7.5, color="#bbbbbb")
fig.tight_layout(rect=(0, 0.085, 1, 1))
fig.savefig(os.path.join(OUT, "Fig2_1_Ventas_CFE_SSB_por_entidad.png"), dpi=200)
plt.close(fig)
m.rename("ventas_SSB_GWh_anual_prom_2006_2024").to_csv(os.path.join(OUT, "datos_fig2_1.csv"), header=True)

# ---------- Figura 2.4 ----------
ga = anual(gen_est, 2002, 2024).fillna(0).mean(axis=1) / 1e3  # GWh/ano
parcial = gen_est.index[gen_est.isna().any(axis=1) | (gen_est == 0).sum(axis=1).gt(12)]
ga = ga.sort_values()
fig, ax = plt.subplots(figsize=(10, 9))
colors = cm.Blues(np.linspace(0.3, 0.95, len(ga)))
bars = ax.barh(ga.index, ga.values, color=colors, edgecolor="black", lw=1)
for b, e in zip(bars, ga.index):
    if e in parcial:
        b.set_hatch("//")
        b.set_alpha(0.55)
ax.xaxis.set_major_formatter(plt.FuncFormatter(miles))
ax.set_xlabel("Generación bruta anual promedio (GWh/año)")
ax.set_title("Generación bruta anual promedio por entidad federativa, 2002–2024 (CFE + PIE)", fontsize=14, pad=12)
ax.grid(axis="x", color=GRID, lw=0.5, alpha=0.5)
nota = "Rayado: cobertura incompleta en la fuente (" + ", ".join(parcial) + ": datos desde marzo de 2017). Sin registro: Aguascalientes, Tabasco, Tlaxcala, Zacatecas."
fig.text(0.01, 0.01, FUENTE + "\n" + nota, fontsize=7.5, color="#bbbbbb")
fig.tight_layout(rect=(0, 0.045, 1, 1))
fig.savefig(os.path.join(OUT, "Fig2_4_Generacion_promedio_por_entidad.png"), dpi=200)
plt.close(fig)
ga.rename("generacion_GWh_anual_prom_2002_2024").to_csv(os.path.join(OUT, "datos_fig2_4.csv"), header=True)

# ---------- Figura 2.5 ----------
g_anual = anual(gen_est, 2006, 2023) / 1e3  # GWh/ano
g_prom = g_anual.mean(axis=1)
c_prom = cons.loc[:, 2006:2023].mean(axis=1)
comp = pd.DataFrame({"ventas_SSB_GWh": c_prom, "generacion_GWh": g_prom.reindex(c_prom.index)})
comp.loc[[e for e in comp.index if e in parcial], "generacion_GWh"] = np.nan  # Morelos fuera de la comparacion
comp["generacion_entre_ventas"] = comp.generacion_GWh / comp.ventas_SSB_GWh
con_gen = comp.dropna().sort_values("generacion_entre_ventas")
sin_gen = comp[comp.generacion_GWh.isna()].sort_values("ventas_SSB_GWh")
orden = list(sin_gen.index) + list(con_gen.index)
fig, ax = plt.subplots(figsize=(10.5, 10))
y = np.arange(len(orden))
ax.barh(y, comp.loc[orden, "ventas_SSB_GWh"], color="#2e86c1", edgecolor="black", lw=0.8, label="Ventas de CFE Suministro Básico (GWh/año)")
ax.scatter(comp.loc[orden, "generacion_GWh"], y, marker="D", s=46, color="#f1c40f", edgecolor="black", zorder=3, label="Generación bruta CFE + PIE (GWh/año)")
for i, e in enumerate(orden):
    r = comp.loc[e, "generacion_entre_ventas"]
    if not np.isnan(r):
        ax.text(max(comp.loc[e, "ventas_SSB_GWh"], comp.loc[e, "generacion_GWh"]) + 500, i, "×%.2f" % r, va="center", fontsize=8, color="#dddddd")
    elif e in parcial:
        ax.text(comp.loc[e, "ventas_SSB_GWh"] + 500, i, "cobertura incompleta", va="center", fontsize=8, color="#ff9f1c")
    else:
        ax.text(comp.loc[e, "ventas_SSB_GWh"] + 500, i, "sin registro de generación", va="center", fontsize=8, color="#ff9f1c")
ax.set_yticks(y)
ax.set_yticklabels(orden, fontsize=8.5)
ax.xaxis.set_major_formatter(plt.FuncFormatter(miles))
ax.set_xlabel("GWh por año (promedio 2006–2023)")
ax.set_title("Ventas de CFE Suministro Básico y generación bruta (CFE + PIE) por entidad federativa, 2006–2023", fontsize=12.5, pad=12)
ax.grid(axis="x", color=GRID, lw=0.5, alpha=0.5)
ax.legend(loc="lower right", facecolor=BG, edgecolor="#555555", labelcolor=FG, fontsize=9)
fig.text(0.01, 0.01, FUENTE + " Ordenado por generación / ventas (×). No es un balance físico: la generación cubre solo CFE y PIE." + "\n" + NOTA_SIE, fontsize=7.5, color="#bbbbbb")
fig.tight_layout(rect=(0, 0.045, 1, 1))
fig.savefig(os.path.join(OUT, "Fig2_5_Ventas_SSB_vs_Generacion.png"), dpi=200)
plt.close(fig)
comp.loc[orden].round(3).to_csv(os.path.join(OUT, "datos_fig2_5.csv"))
total.rename("ventas_SSB_total_GWh").to_csv(os.path.join(OUT, "datos_fig2_2.csv"), header=True)
print("figuras escritas en", OUT, "| estados comparables:", len(con_gen), "| sin generacion:", list(sin_gen.index))
