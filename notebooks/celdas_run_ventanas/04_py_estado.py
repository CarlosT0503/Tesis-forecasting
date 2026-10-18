estado = vt.estado_plan(VENT_DIR, ejecuta="colab")
print(estado.groupby(["ventana", "estado"]).size().unstack(fill_value=0))
print("Total asignado a Colab:", len(estado))
