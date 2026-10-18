import traceback

SESION = "A"   # "A": S4 y S1   |   "B": S2 y S3   (una sesion por pestana)
assert SESION in ("A", "B"), "SESION debe ser 'A' o 'B'"

MIS_VENTANAS = {"A": ["S4", "S1"], "B": ["S2", "S3"]}[SESION]
NIVELES = ["T1", "T2", "T3"]
TIEMPOS = os.path.join(VENT_DIR, "_auditoria", "tiempos_colab_" + SESION + ".csv")

# Cola de esta sesion: solo configuraciones asignadas a Colab (las demas las corre la PC)
cola = []
for nivel in NIVELES:
    for v in MIS_VENTANAS:
        configs = vt.filtrar_por_entorno(vt.construir_configs(nivel, v), "colab")
        if configs:
            cola.append((nivel, v, configs))

total = sum(len(c) for _, _, c in cola)
print("Sesion", SESION, "- ventanas", MIS_VENTANAS, "-", total, "corridas asignadas a Colab")

todos = []
for nivel, v, configs in cola:
    print("")
    print("######## " + nivel + " - " + v + ": " + str(len(configs)) + " configuraciones ########")
    try:
        registros = run_matrix(configs, data_dir=DATA_DIR, mount_drive=False)
    except Exception:
        print("ERROR inesperado en el lote " + nivel + "/" + v + "; se continua con el siguiente lote.")
        print(traceback.format_exc())
        continue
    vt.guardar_tiempos(registros, TIEMPOS)
    todos += registros

resumen = resumen_dataframe(todos)
print(resumen["status"].value_counts())
resumen[resumen["status"] == "failed"][["modelo", "ventana", "run_name", "error"]]
