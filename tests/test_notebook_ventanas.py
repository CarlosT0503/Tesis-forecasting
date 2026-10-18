"""
Pruebas del notebook de Colab (notebooks/run_ventanas.ipynb), sin Colab:

  1. El notebook coincide con sus celdas fuente y TODAS las celdas de codigo
     compilan (ast + compile; las lineas de magia `!`/`%` se omiten).
  2. Las rutas de las celdas coinciden con io_drive.py, y todo `vt.<nombre>` que
     usan las celdas existe en ventanas_tools.
  3. Se EJECUTAN las celdas 2, 3 y 4 en un espacio de nombres controlado:
       - auditoria con regiones faltantes (el caso del KeyError 'problema') y con
         todas presentes (y con los datos reales locales si existen);
       - estado del plan (completa / parcial / no iniciada);
       - lanzamiento: sesiones A y B sin traslape, solo corridas de Colab, todas
         las del plan cubiertas, rutas dentro de Pipeline_Resultados_Ventanas,
         ningun RUN_NAME repetido, y los tiempos se guardan.
  4. Nada de lo anterior escribe en Pipeline_Resultados/ (originales).

    python tests/test_notebook_ventanas.py
"""

import ast
import json
import os
import shutil
import sys
import tempfile
from unittest import mock

import numpy as np
import pandas as pd

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(RAIZ, "src"))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
sys.path.insert(0, os.path.join(RAIZ, "tests"))

for nombre in [
    "optuna", "optuna.samplers", "xgboost", "lightgbm", "tensorflow", "tensorflow.keras",
    "tensorflow.keras.models", "tensorflow.keras.layers", "tensorflow.keras.callbacks",
    "tensorflow.keras.optimizers", "tensorflow.keras.backend",
]:
    sys.modules.setdefault(nombre, mock.MagicMock())

import build_run_ventanas_notebook as bld  # noqa: E402
from tesis_forecast import io_drive, runner, windows  # noqa: E402
from tesis_forecast import ventanas_tools as vt  # noqa: E402
from tesis_forecast.matrix import MatrixRunRecord, resumen_dataframe  # noqa: E402

FALLOS = []


def check(cond, msg):
    print(("  OK   " if cond else "  FALLO ") + msg)
    if not cond:
        FALLOS.append(msg)


def celdas_codigo():
    with open(bld.SALIDA, encoding="utf-8") as f:
        nb = json.load(f)
    return ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]


def ejecutar(codigo, ns):
    exec(compile(bld.sin_magics(codigo), "<celda>", "exec"), ns)


def main():
    print("1. Sintaxis y consistencia del notebook")
    celdas = bld.cargar_celdas()
    bld.validar(celdas)
    check(True, "ast.parse de todas las celdas de codigo")
    codigo = celdas_codigo()
    for i, c in enumerate(codigo, start=1):
        compile(bld.sin_magics(c), "<celda %d>" % i, "exec")
    check(len(codigo) == 7, "%d celdas de codigo compilan (compile())" % len(codigo))
    with open(bld.SALIDA, encoding="utf-8") as f:
        check(json.load(f) == bld.construir(celdas), "run_ventanas.ipynb coincide con notebooks/celdas_run_ventanas/")

    print("\n2. Rutas e importaciones")
    arbol = ast.parse(bld.sin_magics(codigo[0]))
    rutas = {}
    for n in ast.walk(arbol):
        if isinstance(n, ast.Assign) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    rutas[t.id] = n.value.value
    check(rutas["VENT_DIR"] == io_drive.BASE_DIR_VENTANAS, "VENT_DIR == io_drive.BASE_DIR_VENTANAS")
    check(rutas["ORIG_DIR"] == io_drive.BASE_DIR, "ORIG_DIR == io_drive.BASE_DIR (solo lectura)")
    check(rutas["DATA_DIR"] == "/content/drive/MyDrive/Bases de datos Tesis", "DATA_DIR segun docs/DATOS_REQUERIDOS.md")
    check("Pipeline_Resultados_Ventanas" in rutas["VENT_DIR"] and rutas["VENT_DIR"] != rutas["ORIG_DIR"],
          "resultados nuevos y originales en carpetas distintas")
    usados = set()
    for c in codigo:
        for n in ast.walk(ast.parse(bld.sin_magics(c))):
            if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "vt":
                usados.add(n.attr)
    faltan = [a for a in usados if not hasattr(vt, a)]
    check(not faltan, "todo vt.<x> usado existe en ventanas_tools (%s)" % sorted(usados))
    check(all(hasattr(__import__("tesis_forecast.matrix", fromlist=["x"]), a) for a in ("run_matrix", "resumen_dataframe")),
          "run_matrix y resumen_dataframe importables")

    tmp = tempfile.mkdtemp(prefix="test_nb_")
    try:
        vent = os.path.join(tmp, "Pipeline_Resultados_Ventanas")
        os.makedirs(os.path.join(vent, "_auditoria"))
        base_ns = {"os": os, "vt": vt, "VENT_DIR": vent, "ORIG_DIR": os.path.join(tmp, "Pipeline_Resultados"),
                   "resumen_dataframe": resumen_dataframe, "__builtins__": __builtins__}

        print("\n3. Celda 2 (auditoria) con regiones faltantes y completas")
        from test_windows import construir_datos  # datos sinteticos: CEN y NES completas, BCA corta
        datos = os.path.join(tmp, "datos")
        os.makedirs(datos)
        construir_datos(datos)
        ns = dict(base_ns, DATA_DIR=datos)
        try:
            ejecutar(codigo[1], dict(ns))  # celda 2 de codigo
            check(True, "celda 2 se ejecuta con regiones faltantes (sin KeyError 'problema')")
        except Exception as e:
            check(False, "celda 2 con regiones faltantes: %s: %s" % (type(e).__name__, e))
        check(os.path.exists(os.path.join(vent, "_auditoria", "plan_corridas_ventanas.csv")), "celda 2 guarda el plan")
        datos_reales = os.path.join(RAIZ, "datos_locales")
        if os.path.isdir(datos_reales):
            try:
                ejecutar(codigo[1], dict(base_ns, DATA_DIR=datos_reales))
                check(True, "celda 2 se ejecuta con los datos reales locales (todas las regiones presentes)")
            except Exception as e:
                check(False, "celda 2 con datos reales: %s: %s" % (type(e).__name__, e))
        else:
            print("  (datos_locales/ no existe: se omite la prueba con datos reales)")

        print("\n4. Celda 3 (estado) y reanudacion")
        plan = vt.plan_dataframe(ventanas=["S4"])
        colab = plan[plan["ejecuta_en"] == "colab"].reset_index(drop=True)
        run_completa, run_parcial = colab.loc[0, "run_name"], colab.loc[1, "run_name"]
        for nombre, regiones in [(run_completa, ["BCA", "CEN", "NES", "NOR", "NTE", "OCC", "ORI", "PEN"]), (run_parcial, ["BCA", "CEN"])]:
            d = os.path.join(vent, "S4", nombre)
            os.makedirs(d)
            json.dump({"modelo": "x"}, open(os.path.join(d, "config.json"), "w"))
            pd.DataFrame({"region": regiones, "MAE": 1.0, "RMSE": 1.0, "MAPE": 1.0, "sMAPE": 1.0}).to_csv(os.path.join(d, "metricas.csv"), index=False)
            pd.DataFrame({"x": [1]}).to_csv(os.path.join(d, "series.csv"), index=False)
        ns3 = dict(base_ns)
        ejecutar(codigo[2], ns3)
        est = ns3["estado"]
        s = est[est["ventana"] == "S4"].set_index("run_name")["estado"]
        check(s[run_completa] == "completa" and s[run_parcial] == "parcial", "estado_plan distingue completa / parcial")
        check((est["estado"] == "no_iniciada").sum() == len(est) - 2 and len(est) == 28 * 4, "las demas corridas de Colab figuran no iniciadas (112 en total)")

        print("\n5. Celda 4 (lanzamiento): sesiones A y B")
        llamadas = {}
        for sesion in ("A", "B"):
            registrados = []

            def run_matrix_falso(configs, data_dir=None, mount_drive=False, _r=registrados):
                recs = []
                for c in configs:
                    r = runner.resolve_run(c)
                    recs.append(MatrixRunRecord(c, r.run_name, "completed", 1.0, None, r.run_dir, duracion_s=0.1))
                _r.append(list(configs))
                return recs

            ns4 = dict(base_ns, DATA_DIR=datos, run_matrix=run_matrix_falso)
            ejecutar(codigo[3].replace('SESION = "A"', 'SESION = "%s"' % sesion), ns4)
            cfgs = [c for lote in registrados for c in lote]
            llamadas[sesion] = cfgs
            check(set(ns4["MIS_VENTANAS"]) == ({"S4", "S1"} if sesion == "A" else {"S2", "S3"}),
                  "sesion %s procesa %s" % (sesion, ns4["MIS_VENTANAS"]))
            check(all(vt.ejecuta_en(c.modelo) == "colab" for c in cfgs), "sesion %s: solo modelos de Colab (redes)" % sesion)
            check(len(cfgs) == 56, "sesion %s lanza %d corridas (esperadas 56)" % (sesion, len(cfgs)))
            check(os.path.exists(os.path.join(vent, "_auditoria", "tiempos_colab_%s.csv" % sesion)), "sesion %s guarda tiempos" % sesion)
            niveles_en_orden = [ns4["cola"][i][0] for i in range(len(ns4["cola"]))]
            check(niveles_en_orden == sorted(niveles_en_orden), "sesion %s: orden de niveles T2 antes que T3" % sesion)
        claves = lambda cs: {(c.ventana, runner.resolve_run(c).run_name) for c in cs}
        a, b = claves(llamadas["A"]), claves(llamadas["B"])
        check(not (a & b), "sesiones A y B sin traslape")
        plan_colab = {(r.ventana, r.run_name) for r in vt.plan_dataframe().query("ejecuta_en == 'colab'").itertuples()}
        check((a | b) == plan_colab and len(plan_colab) == 112, "A u B cubren exactamente las 112 corridas de Colab del plan")
        todas = [runner.resolve_run(c) for c in llamadas["A"] + llamadas["B"]]
        check(all(r.run_dir.replace(os.sep, "/").startswith(io_drive.BASE_DIR_VENTANAS) for r in todas),
              "todas las rutas dentro de Pipeline_Resultados_Ventanas/")
        check(not any(r.run_dir.replace(os.sep, "/").startswith(io_drive.BASE_DIR + "/") for r in todas),
              "ninguna ruta dentro de Pipeline_Resultados/ (originales)")
        check(len({(r.ventana, r.run_name) for r in todas}) == len(todas), "ningun RUN_NAME repetido dentro de una ventana")

        print("\n6. La PC y Colab no se pisan")
        local = {(r.ventana, r.run_name) for r in vt.plan_dataframe().query("ejecuta_en == 'local'").itertuples()}
        check(not (local & plan_colab) and len(local) + len(plan_colab) == 216, "PC (104) + Colab (112) = 216 sin interseccion")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n" + ("TODO OK" if not FALLOS else "%d FALLO(S): %s" % (len(FALLOS), FALLOS)))
    return 1 if FALLOS else 0


if __name__ == "__main__":
    sys.exit(main())
