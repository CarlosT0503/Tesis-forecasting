# Anomalía de LSTM directa: regiones con 20 intentos de Optuna frente a un presupuesto de 10

Fecha: 2026-10-22. Estado: **análisis documental; no se ha borrado, modificado ni repetido nada.** La herramienta de auditoría de solo lectura (`scripts/auditar_trials_lstm_directa.py`, con su prueba) se publicó en el commit `9863248`, con autorización del autor. **La auditoría todavía no se ha ejecutado**: las bases `optuna_lstm_directa.db` viven en el Drive de Colab y no hay ninguna copia local (búsqueda en el repositorio, Descargas y Documentos: ninguna). Hasta que el autor la ejecute, no se sabe cuántas regiones tienen más de 10 intentos ni si el exceso cambió la selección.

## 1. Qué se observó

El informe de progreso de Colab (celda 3, 22/10) muestra que el estudio de LSTM directa de **S4 / Temperatura / región NTE** tiene **20 intentos** de Optuna, frente al presupuesto de 10 por región que fija el plan de corridas (`docs/plan_corridas_ventanas.csv`, columna de intentos). La observación es del autor sobre su Drive; yo no tengo acceso a esas bases, así que **no sé cuántas regiones más están en el mismo caso**. Eso es lo que debe medir la auditoría de la sección 4.

## 2. Mecanismo (verificado en el código)

`tune_lstm` en `src/tesis_forecast/models/lstm_direct.py` abre el estudio de Optuna con `load_if_exists=True` (un estudio por región y configuración, guardado en `optuna_lstm_directa.db` dentro de la carpeta de la corrida).

- **Código anterior al commit 608ca6a (20/10):** llamaba `study.optimize(n_trials=n_trials)`. Optuna interpreta `n_trials` como intentos **adicionales**, no como total. Si una región había terminado sus 10 intentos y la corrida se cortó *después* (entrenamiento final, guardado de la región, reinicio de Colab, desconexión) sin quedar marcada como completa, la reanudación volvía a ejecutar `tune_lstm`, encontraba los 10 intentos en la base y añadía otros 10 (10 + 10 = 20). Una región cortada a la mitad de la búsqueda (k intentos) acababa con k + 10.
- **Código actual (608ca6a):** calcula `pendientes = n_trials − (intentos COMPLETE)` y solo ejecuta esos. Evita que **vuelva a ocurrir**; no revierte lo ya guardado.
- **Consecuencia importante:** si se relanza hoy S4/Temp/NTE con el código actual, `pendientes = 0`, no se ejecuta ningún intento y `study.best_params` se calcula sobre **los 20** de la base. La corrección no elimina la anomalía de los estudios existentes; la mantiene.

## 3. Qué efecto tiene (y qué no se sabe)

| Aspecto | Valoración |
|---|---|
| **Fuga de información del periodo de prueba** | **No.** El objetivo de Optuna se evalúa con las últimas 168 h del *entrenamiento* (`objective_lstm`: holdout interno `train_y[:-168]` y validación sobre `train_y[origin:origin+168]`). Los intentos extra no usan datos de prueba. |
| **Ventaja de presupuesto** | **Sí, acotada.** La región con 20 intentos tuvo el doble de oportunidades de encontrar buenos hiperparámetros que las otras. Como `best_params` es el mejor de todos los intentos, su valor de validación nunca es peor que el del mejor de los 10 primeros. |
| **¿Cambió la selección?** | **Depende de dónde cayó el mejor intento.** Si está entre los intentos 0–9, los hiperparámetros elegidos serían los mismos con presupuesto 10 y la anomalía **no tuvo efecto** en la selección. Si está entre el 10 y el 19, la selección sí cambió. Con la base a la vista es una lectura directa, sin reentrenar. |
| **Efecto en la métrica de prueba** | No es calculable sin reentrenar: la mejora en validación no implica mejora en prueba. Un intento extra puede incluso empeorar el resultado por sobreajuste a la validación. |
| **Comparabilidad** | Una celda (config × región) con presupuesto distinto no es estrictamente comparable con las demás. Si son pocas y no cambian la selección, el efecto es nulo; si cambian la selección, merecen una nota. |
| **Reproducibilidad exacta** | No garantizada: TensorFlow no está fijado de forma determinista; aunque `TPESampler(seed=42)` repite la secuencia de hiperparámetros propuestos, los valores de validación de un reentrenamiento pueden diferir ligeramente. Por eso "rehacer con presupuesto 10" no reproduciría bit a bit lo que habría salido sin la anomalía. |

## 4. Auditoría de solo lectura (sin entrenar, sin escribir en las corridas)

`scripts/auditar_trials_lstm_directa.py` recorre todas las bases `optuna_lstm_directa.db` bajo `Pipeline_Resultados_Ventanas` y, por estudio, informa: intentos completos / fallidos / otros, el mejor valor de validación entre los primeros 10 y entre todos, en qué intento está cada uno, si el mejor cae **fuera** de los 10 primeros, la diferencia de validación y si los hiperparámetros elegidos coinciden. Abre SQLite en modo `ro` con `query_only`, no importa Optuna ni TensorFlow y se niega a escribir su informe dentro de una carpeta de corrida (solo fuera de `Pipeline_Resultados_Ventanas` o en `_auditoria`).

Verificada con bases Optuna reales (10 intentos; 20 con el mejor entre los primeros 10; 20 con el mejor en el intento 11; 10 + 10 reanudado), comprobando además que el hash de la base no cambia (`tests/test_auditar_trials_lstm_directa.py`).

**Cómo usarla en Colab** (una celda nueva al final del cuaderno, sin tocar las existentes; requiere que el repositorio en Colab tenga el script, es decir, `git pull` después de publicarlo):

```python
!python /content/tesis_repo/scripts/auditar_trials_lstm_directa.py \
    --base-ventanas /content/drive/MyDrive/Pipeline_Resultados_Ventanas \
    --salida /content/drive/MyDrive/Pipeline_Resultados_Ventanas/_auditoria/trials_lstm_directa.csv
```

Es seguro ejecutarla mientras corre otra celda; solo lee. Si el autor prefiere no actualizar el repositorio de Colab durante la sesión en curso, puede pegar el script en una celda.

## 5. Opciones de tratamiento (ninguna borra resultados)

| # | Opción | Qué implica | Costo | Cuándo conviene |
|---|---|---|---|---|
| T0 | **Documentar sin cambios** | Dejar las corridas como están y registrar en un anexo qué regiones tuvieron más de 10 intentos y si la selección cambió | Ninguno | Si el mejor cae en los primeros 10 (la anomalía no tuvo efecto), o son muy pocas celdas |
| T1 | **Marcar sin tocar los resultados** | Un CSV auxiliar (`presupuesto_excedido`) con las celdas afectadas, **separado** de `metricas.csv`/`series.csv`; los consolidados las señalan con nota. Declarar la limitación en el texto | Ninguno de cómputo; algo de redacción | Si hay celdas donde la selección sí cambió y no se quiere repetir nada |
| T2 | **Recalcular solo el ajuste final con el mejor de los 10 primeros** | Para cada región afectada, un único entrenamiento final con los hiperparámetros del mejor entre los intentos 0–9 (ya en la base), guardado en una carpeta nueva con sufijo propio (p. ej. `_p10`); el original se conserva intacto y se comparan | Un entrenamiento final por región afectada (no 10 intentos de búsqueda); el tiempo depende de la GPU y no lo he medido | Solo si la auditoría muestra cambios de selección en celdas que importan para el ranking, y el autor lo autoriza |
| T3 | Excluir las celdas afectadas de los rankings | Pierde datos válidos y no hace falta: no hay fuga | — | No recomendada |
| T4 | Borrar los intentos 11–20 de la base y volver a ajustar | Altera evidencia; contradice la instrucción de no borrar resultados | — | **Descartada** |

**Recomendación:** ejecutar primero la auditoría (T0 con las evidencias). Si hay celdas donde la selección cambió, aplicar T1 y plantear T2 al autor con la lista concreta. La decisión sobre cuál versión entra a los rankings (original marcada o recalculada) debe fijarse **antes** de ver las métricas de prueba de T2, para no elegirla según el resultado.

## 6. Redacción propuesta (condicionada a lo que muestre la auditoría)

Para el capítulo de metodología o limitaciones, **solo si hay celdas afectadas**:

> En la LSTM directa, algunas búsquedas de hiperparámetros reanudadas tras una interrupción ejecutaron más intentos que el presupuesto previsto (10 por región). En N celdas de las M evaluadas (lista en el anexo) el mejor intento quedó fuera de los diez primeros. La validación de Optuna usa solo las 168 horas finales del entrenamiento, por lo que el exceso no incorpora información del periodo de prueba; en cambio, estas celdas disponen de un presupuesto de búsqueda mayor y su comparación con las demás debe leerse con esa salvedad. El problema se corrigió en el código antes de completar las corridas restantes.

Si la auditoría muestra que en ninguna celda el exceso cambió la selección, basta una línea en la nota metodológica o en el anexo de trazabilidad. Los números N y M no se conocen todavía.

## 7. Pendiente

1. Que el autor ejecute la celda de la sección 4 (tras `git pull` en Colab, o pegando el script) y comparta la salida o el CSV `_auditoria/trials_lstm_directa.csv`; con ella se completan N y M.
2. Decidir T0/T1/T2 con la lista real.
3. Verificar si otras redes (FCNN, LSTM residual, Ensemble STL) pudieron tener el mismo efecto: **no**, según el código, porque sus funciones `tunear_*` ya calculaban `remaining = n_trials − completos` antes de esta corrección. Lo que sí hacen al reanudar es repetir el entrenamiento final de la región (no la búsqueda), con un estado aleatorio distinto al de una corrida ininterrumpida; eso no modifica hiperparámetros.
