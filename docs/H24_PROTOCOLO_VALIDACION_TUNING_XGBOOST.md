# H24 — Protocolo para validar la corrección del ajuste de hiperparámetros de XGBoost

Fecha: 2026-10-22. Estado: **propuesta para aprobación del autor. No se ha ejecutado nada, no se modificó código, configuraciones ni resultados, y no se lanzó ningún experimento en la PC.**

Objetivo: decidir con evidencia, y **sin usar el conjunto de prueba para elegir hiperparámetros ni procedimientos**, cómo corregir el hecho de que el ajuste de hiperparámetros de XGBoost no opera con 336 h de entrenamiento (H24), y validar la solución en varias regiones y semanas.

## 1. Punto de partida (hechos verificados)

| Hecho | Evidencia |
|---|---|
| Con `train_hours=336` y `forecast_horizon=168`, el tuning de XGBoost dispone de 168 h (`tune_train_y`) y usa una ventana fija de 168 rezagos (`WINDOW_DEFAULT`): `create_feature_df` devuelve **0 filas** y `objective_xgboost` retorna `inf` (`if len(df_train) < 50`). | `xgboost_model.py` (`objective_xgboost`, `_preparar_serie`: `window_tune = WINDOW_DEFAULT`); H24 (verificado ejecutando la función) |
| Las 28 corridas XGBoost de S1–S4 (7 configuraciones × 4 semanas, 10 intentos por región) tienen todos sus intentos en `inf`; las 8 regiones de cada corrida usan el mismo conjunto de parámetros, el del intento 0. | H24 (conteo sobre los resultados) y `docs/plan_corridas_ventanas.csv` |
| LightGBM sí ajusta: `_resolver_window(336, 168)` da `min(168, max(24, (336−168)//2)) = 84` rezagos, de modo que el tuning dispone de 168 − 84 = 84 filas (≥ 50). (Cálculo aritmético sobre el código; no ejecutado aquí.) | `lightgbm_model.py` (`_resolver_window`) |
| **Piloto E** (CEN, exógena Generación, semana S4, 80 intentos): al ajustar con 504 h de historia (336 de entrenamiento, 168 de validación; reentrenar con las 336 h previas a la prueba), la sMAPE de **validación** mejoró (2.41 sin tuning, 2.16 con los primeros 10 intentos, 1.90 con los 80), pero la sMAPE de **prueba** empeoró (3.34, 3.56, 3.68). | `docs/correcciones_tesis/H24_piloto_E/` (`informe_CEN_Generacion.json`) |
| Con los mismos parámetros, las predicciones de XGBoost son idénticas entre las configuraciones Temp, IGAE, Imp y Exp (el piloto lo comprobó bit a bit). | Log del piloto; relevante para §6.4 de la tesis |
| Datos disponibles: las ocho regiones tienen demanda horaria del 2019-01-01 al 2026-05-23, es decir, hay semanas de sobra anteriores a S1 (2026-04-26). | Lectura de `datos_locales/*_long.csv` (22/10) |

**Lectura prudente del piloto:** es **una** región, **una** exógena y **una** semana; no demuestra que ajustar empeore, pero sí que una mejora de la validación de 168 h no implica una mejora en prueba (validación ruidosa o sobreajuste a esa ventana). Por eso el protocolo mide esa relación en lugar de suponerla. Además, la prueba de CEN/Generación en S4 **ya fue vista** con tres procedimientos, así que se **excluye de cualquier decisión** (regla R5).

## 2. Reglas anti-fuga (obligatorias; se fijan antes de ver resultados)

| # | Regla |
|---|---|
| R1 | Ninguna hora de prueba de S1–S4 (2026-04-26 a 2026-05-23) interviene en elegir hiperparámetros **ni** el procedimiento de ajuste. |
| R2 | Los hiperparámetros de cada corrida se eligen solo con datos anteriores a su origen de pronóstico (validación dentro de la historia). |
| R3 | El procedimiento se elige con **semanas de desarrollo** que terminan antes de S1 (todas las horas < 2026-04-26 00:00): ahí sí se mira el error de "prueba de desarrollo". S1–S4 nunca se usan para elegir. |
| R4 | La regla de decisión (sección 6), los umbrales y las métricas se fijan y se firman antes de calcular nada. |
| R5 | Se excluye de la decisión la prueba de CEN/Generación/S4 (vista en el piloto). |
| R6 | La fase confirmatoria sobre S1–S4 se ejecuta **una sola vez** con el procedimiento ya congelado; se reportan todos los resultados, sin reelegir. |
| R7 | Todos los candidatos reciben el mismo presupuesto de intentos (10, como en el plan) y la misma semilla del muestreador (`TPESampler(seed=42)`). |
| R8 | Ninguna corrida del protocolo escribe en las carpetas de resultados existentes; salida en carpetas nuevas con sufijo propio. |

## 3. Procedimientos candidatos

Todos comparten el modelo (XGBoost), el espacio de búsqueda, la métrica objetivo (sMAPE) y el pronóstico recursivo de 168 h; difieren solo en cómo se ajusta.

| Id | Procedimiento | Qué cambia | Datos que usa antes de la prueba |
|---|---|---|---|
| **C0** | **Actual** (referencia): el tuning devuelve `inf`; se usan los parámetros del intento 0 | — | 336 h |
| **C1** | **Ventana adaptativa** (regla de LightGBM): rezagos = 84 en lugar de 168, mismo reparto 168 + 168 | Cambia también la estructura del modelo final (84 rezagos), no solo el ajuste | 336 h |
| **C2** | **Piloto E**: tuning con 336 h, validación en las 168 h siguientes; reentrenar con las 336 h inmediatamente anteriores a la prueba; rezagos 168 | Usa 168 h más de historia para elegir; el ajuste final usa las mismas 336 h | 504 h |
| **C3** | **E con dos bloques de validación** (opcional): 336 h de ajuste, dos bloques sucesivos de 168 h de validación, se promedia la sMAPE; reentrenar con las últimas 336 h | Reduce el ruido de una sola ventana de validación | 672 h |
| **C4** | **Sin ajuste**: parámetros por defecto de la biblioteca (referencia de "declarar la limitación honestamente") | No hay búsqueda | 336 h |
| **CL** | LightGBM tal como está (hermano de referencia, no candidato) | — | 336 h |

C1 y C2 son los candidatos naturales; C3 solo si C2 muestra el problema de ruido del piloto; C4 y C0 son las referencias que una corrección debe superar.

## 4. Diseño

**Semanas de desarrollo** (domingo–sábado, igual que S1–S4), todas anteriores a S1:

| Id | Prueba de desarrollo |
|---|---|
| D1 | 29 mar – 4 abr 2026 |
| D2 | 5 – 11 abr 2026 |
| D3 | 12 – 18 abr 2026 |
| D4 | 19 – 25 abr 2026 |

Para D1 el candidato C3 necesitaría datos desde unas 672 h antes (≈ 1 mar), disponibles según la lectura de los datos.

**Regiones:** las ocho (BCA, CEN, NES, NOR, NTE, OCC, ORI, PEN), para que la conclusión no dependa de una región.

**Exógenas:** dos configuraciones, **Generación** (donde, según el piloto, la exógena sí cambia las predicciones) y **Temperatura**. Las demás (IGAE, Imp, Exp) dan predicciones idénticas a Temp con los mismos parámetros, así que no aportan información independiente.

**Unidades:** 8 regiones × 4 semanas × 2 exógenas = **64 unidades por candidato**; con C0, C1, C2, C3, C4 y CL son 384 corridas de desarrollo.

**Presupuesto de cómputo (estimación, no medida para este diseño):** el piloto tardó 547 s en 80 intentos de Optuna (≈ 6.8 s por intento, un hilo, con la PC cargada). Con 10 intentos por unidad, más el ajuste final, el orden es de **1 a 2 minutos por corrida**, es decir, **unas 6 a 12 horas** de un solo hilo para las 384, **paralelizables** (cada unidad es independiente). **No se lanza en la PC mientras trabaja SARIMAX**; opciones: Colab (CPU basta) o la PC al terminar la cola.

**Sensibilidad al presupuesto (subconjunto):** repetir el candidato ganador con 40 intentos en 16 unidades (2 exógenas × 4 regiones × 2 semanas elegidas por sorteo con semilla registrada), para comprobar si más intentos mejoran la validación pero no la prueba de desarrollo, como sugiere el piloto.

## 5. Métricas y análisis

**Métrica principal:** sMAPE en la prueba de desarrollo (es la métrica que se optimiza; se reportan también MAE, RMSE y MAPE).

**Comparación pareada:** para cada candidato y unidad, Δ = sMAPE(candidato) − sMAPE(referencia), con referencia C4 y C0. Se resume por la media y la mediana de Δ y se estima un intervalo de confianza al 95 % con *bootstrap* por bloques (el bloque es la pareja región × semana, promediando las dos exógenas, porque están correlacionadas; 32 bloques). También: proporción de unidades en que el candidato gana y resultados **por región**.

**Diagnósticos del tuning (qué respondió el piloto sin querer):**

1. *Relación validación–prueba:* en un subconjunto de 16 unidades, para cada uno de los 10 intentos, se calcula la sMAPE de prueba de desarrollo (solo semanas de desarrollo, nunca S1–S4) y se mide la correlación de rangos con la sMAPE de validación. Si es ≈ 0, ajustar sobre 168 h no sirve para este problema y el hallazgo es en sí mismo un resultado.
2. *Brecha de sobreajuste:* sMAPE de prueba − sMAPE de validación, por candidato.
3. *Estabilidad de la selección:* dispersión de los parámetros elegidos entre semanas de una misma región; si cambian mucho con validaciones casi iguales, la elección es ruido.
4. *Intentos finitos:* proporción de intentos con valor finito (debe ser ≈ 100 %; la ausencia de esto fue la causa de H24).

## 6. Regla de decisión (a fijar antes de ejecutar; los umbrales los propone el autor)

1. **Candidatos elegibles:** C1, C2 y, si se corrió, C3.
2. **Adopción:** un candidato se adopta si (a) su Δ medio frente a C4 es negativo con IC 95 % que **excluye 0** y (b) su Δ medio frente a C0 es negativo con IC que excluye 0.
3. **Salvaguarda por región:** si en alguna región el candidato empeora frente a C4 en más de un **5 % relativo** (umbral propuesto, a confirmar), se reporta y se discute; no veta la adopción por sí solo.
4. **Desempate:** entre candidatos que cumplen, se prefiere el más simple y el que usa menos historia (C1 antes que C2, C2 antes que C3).
5. **Si ninguno cumple (a) y (b):** no se corrige el procedimiento; se **declara la limitación**. Aun así se propone sustituir "parámetros del primer intento aleatorio" (C0) por **parámetros por defecto** (C4), porque un sorteo arbitrario no es una configuración defendible; esa sustitución también es decisión del autor.
6. Los criterios de la sección 5 (diagnósticos) **no** deciden: informan la interpretación.

## 7. Fase confirmatoria (solo después de congelar el procedimiento)

1. Implementar el procedimiento elegido de forma aislada (nuevo script, sin tocar `xgboost_model.py` hasta aprobación expresa del cambio), como el piloto E.
2. Ejecutarlo **una vez** sobre las 28 corridas XGBoost de S1–S4, guardando en carpetas nuevas con sufijo propio (p. ej. `_tuningfix`); las 28 corridas actuales se conservan intactas.
3. Reportar ambos conjuntos en la tesis: versión inicial (parámetros del primer intento) y versión con el procedimiento validado, con el protocolo que condujo a la elección. Sin reelegir tras ver S1–S4.
4. Comparar el XGBoost corregido con LightGBM y con los demás modelos con las mismas métricas.
5. Hipótesis a contrastar (no a confirmar): que el tuning efectivo mejora a XGBoost en S1–S4 frente a C0; de no ser así, se reporta tal cual.

## 8. Verificaciones técnicas previas (no alteran resultados existentes)

Pruebas automáticas, con datos sintéticos o de solo lectura, **antes** de cualquier corrida de desarrollo:

| # | Verificación | Qué demuestra |
|---|---|---|
| V1 | Causalidad: las variables de la hora *t* usan solo datos ≤ *t*−1 en entrenamiento, validación y pronóstico (como B1 del piloto) | Sin fuga temporal |
| V2 | Perturbación: cambiar al azar los valores de las 168 h de prueba y comprobar que los hiperparámetros elegidos y el modelo reentrenado no cambian (como B2) | La prueba no influye en la elección |
| V3 | Aritmética de filas: para cada candidato, filas utilizables del tuning ≥ 50 y validación completa | Evita repetir el defecto de H24 |
| V4 | Alarma de intentos: si todos los intentos de una región son `inf`, la corrida **falla de forma explícita** en lugar de continuar con el intento 0 | Evita que el problema vuelva en silencio |
| V5 | Exógenas en validación estimadas con la misma regla que en prueba (como B3) | Sin ventaja de información |
| V6 | Reproducibilidad: dos ejecuciones con la misma semilla dan los mismos parámetros | Resultado auditable |
| V7 | Ningún dato posterior a 2026-04-26 00:00 entra en las semanas de desarrollo | Cumple R1 y R3 |
| V8 | Ningún archivo de resultados existente cambia (hash antes y después) | Cumple R8 |

Ya hecha (solo lectura): disponibilidad de historia, ocho regiones con datos 2019-01-01 a 2026-05-23.

## 9. Puntos de autorización

| Punto | Qué se aprueba | Quién |
|---|---|---|
| A1 | Este protocolo, los candidatos, las semanas de desarrollo, la regla de decisión y los umbrales (en particular el 5 %) | Autor |
| A2 | Escribir el script aislado de desarrollo y sus pruebas V1–V8 | Autor |
| A3 | Ejecutar la fase de desarrollo (dónde y cuándo: Colab o PC libre) | Autor |
| A4 | Aplicar la regla de decisión con los resultados y congelar el procedimiento | Autor |
| A5 | Cambiar `xgboost_model.py` (si el procedimiento lo requiere) y ejecutar la fase confirmatoria | Autor |

## 10. Limitaciones del diseño

- **Cuatro semanas de desarrollo** dan poca potencia estadística; por eso se usan ocho regiones y se reportan intervalos, no solo medias. Si los intervalos son anchos, el resultado es "no concluyente", que equivale a declarar la limitación.
- **Estacionalidad:** las semanas de desarrollo son de abril y las de prueba de abril–mayo; calor y demanda de mayo pueden diferir.
- **Exógenas:** que cuatro de ellas den predicciones idénticas con los mismos parámetros es un hecho sin explicar (relevante para §6.4); **este protocolo no lo explica**.
- **C1 confunde dos cambios** (ventana de 84 rezagos y tuning efectivo). Si C1 gana, no se sabrá cuál de los dos aporta; si importara, se añadiría C1' (ventana 84 con parámetros por defecto).
- **Corte de las exógenas:** las exógenas globales terminan el 2026-03-31 (corte común deliberado del proyecto), de modo que casi toda la ventana de desarrollo cae después de ese corte, igual que S1–S4. Antes de ejecutar hay que **verificar cómo trata el pipeline esas semanas** (verificación V5) y usar exactamente el mismo tratamiento.
- **Interacción con H27:** ambos hallazgos tratan de presupuesto de búsqueda; las conclusiones sobre cuántos intentos importan en XGBoost no se trasladan sin más a la LSTM directa.
- **Corridas originales de agosto–septiembre (Colab):** no se sabe si tenían el mismo comportamiento; no se investiga aquí.

## 11. Decisiones que necesito del autor

1. ¿Se aprueban los candidatos (C1, C2, C3 opcional, referencias C0 y C4) y las semanas de desarrollo D1–D4?
2. ¿Umbral de la salvaguarda por región: 5 % relativo u otro?
3. ¿Exógenas de desarrollo: Generación y Temperatura?
4. ¿Se incluye C3 desde el inicio o solo si C2 muestra el problema del piloto?
5. ¿Dónde se ejecutará la fase de desarrollo (Colab, o la PC cuando termine SARIMAX)?
6. ¿Se acepta sustituir C0 por C4 como configuración por defecto si ningún candidato cumple la regla?
