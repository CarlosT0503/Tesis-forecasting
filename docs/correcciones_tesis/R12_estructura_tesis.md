# R12 — Estructura del trabajo y relación con los objetivos

| Campo | Contenido |
|---|---|
| **Observación que resuelve** | R12 (Roberto): describir la estructura del trabajo y cómo se relaciona con los objetivos. |
| **Estado** | Redacción preparada (2026-10-20). **No integrada** en `tesis.tex`. |
| **Ubicación propuesta** | Introducción, nueva §0.4 "Estructura del documento", después de §0.3 "Alcance y delimitaciones". |
| **Fuente de los títulos** | PDF vigente `Series_de_Tiempo_para_la_Predicción_de_Consumo_Eléctrico (11).pdf` (índice y texto). `tesis.tex` no está en este repositorio; antes de integrar, confirmar que sus títulos coinciden con los del PDF. |
| **Depende de** | Que R13 (Cap. 5), R14–R16 (Cap. 2) y el consolidado de S1–S4 (Caps. 6–7) se integren: el texto describe el contenido **ya con esas correcciones** y las marca donde cambian el capítulo. R19 (renombrar "Metodología" a "Experimentación") cambiaría el título del Cap. 5: aquí se usa el título actual. |

## Parte A — Texto propuesto (listo para integrar)

### 0.4. Estructura del documento

El trabajo se organiza en siete capítulos, además de esta introducción. Los capítulos 1 a 4 construyen el marco necesario para plantear el problema; el 5 describe cómo se resolvió; el 6 presenta lo que se obtuvo; y el 7 responde a la pregunta de investigación.

**Capítulo 1. Estado del Arte.** Revisa la literatura sobre pronóstico de demanda eléctrica organizada en torno a las decisiones que plantea el problema: el uso de métodos univariados frente a métodos con variables explicativas, el papel de la temperatura y de otras variables exógenas, los algoritmos de aprendizaje automático y las redes neuronales, y la descomposición STL como parte del diseño del predictor. Los antecedentes muestran que la ventaja de una familia de modelos depende del horizonte, de la escala del problema y de las variables empleadas, lo que justifica una comparación empírica bajo condiciones comunes.

**Capítulo 2. Generación Eléctrica en México.** Describe los datos y el sistema eléctrico que se estudia: las fuentes de información (CENACE, SENER-SIE, INEGI), la diferencia entre generación, consumo y demanda, el origen y la distribución territorial de la generación y del consumo, y la organización del sistema en regiones de control. Presenta además las ocho series que se pronostican y delimita el alcance geográfico del estudio (las siete regiones del Sistema Interconectado Nacional y el sistema de Baja California).

**Capítulo 3. Series de Tiempo.** Expone los fundamentos estadísticos: los componentes de una serie, la estacionariedad y los modelos ARIMA y SARIMA. Aporta la base de los modelos estadísticos y de las estrategias que modelan por separado tendencia, estacionalidad y residuo.

**Capítulo 4. Machine Learning y Deep Learning.** Presenta los fundamentos del aprendizaje supervisado, el gradient boosting (XGBoost y LightGBM), el perceptrón multicapa y la red LSTM, y el procesamiento específico de series de tiempo (particiones temporales, valores faltantes y atípicos).

**Capítulo 5. Metodología.** Describe el diseño experimental: la obtención y preparación de los datos, las variables exógenas y su tratamiento, las cuatro semanas de prueba y la longitud de entrenamiento por familia, cada uno de los modelos y las métricas de evaluación (MAE, RMSE, MAPE y sMAPE).

**Capítulo 6. Resultados experimentales.** Compara los modelos bajo condiciones comunes y responde tres preguntas: si los modelos más complejos obtienen mejores pronósticos, si las variables exógenas mejoran el pronóstico y si existe un modelo adecuado para todas las regiones. Distingue los resultados comparables de los obtenidos bajo otras condiciones temporales y analiza la estabilidad de las diferencias entre semanas.

**Capítulo 7. Conclusiones.** Responde a la pregunta de investigación, señala las limitaciones del estudio y propone líneas de trabajo futuro.

**Relación con los objetivos.** La siguiente tabla indica en qué capítulos se desarrolla cada objetivo específico.

| Objetivo | Se fundamenta en | Se desarrolla en | Se responde en |
|---|---|---|---|
| **O1.** Integrar las series horarias de demanda con las variables exógenas en un conjunto alineado temporalmente. | Cap. 2 (fuentes y definición de las variables) | Cap. 5 (obtención y preparación de datos, variables exógenas) | Cap. 5 (conjunto de datos resultante) |
| **O2.** Implementar modelos de referencia y modelos estadísticos, de gradient boosting y de redes neuronales, univariados y con exógenas, optimizando hiperparámetros cuando corresponda. | Caps. 1, 3 y 4 | Cap. 5 (modelos y búsqueda de hiperparámetros) | Cap. 6 (desempeño de cada modelo) |
| **O3.** Implementar estrategias basadas en la descomposición STL y contrastarlas con el modelado directo. | Cap. 1 (antecedentes de STL) y Cap. 5 | Cap. 5 (estrategias con STL) | Cap. 6 (§6.2: modelos híbridos frente a modelos directos) |
| **O4.** Evaluar el efecto de las variables exógenas, individuales y combinadas, en cada familia de modelos. | Cap. 1 (temperatura y otras variables) | Cap. 5 (matriz de variables exógenas) | Cap. 6 (§6.4) y Cap. 7 |
| **O5.** Comparar las estrategias con MAE, RMSE, MAPE y sMAPE fuera de muestra, global y por región, analizando las diferencias y su estabilidad. | Cap. 5 (métricas y ventanas) | Cap. 6 | Cap. 6 (§6.2, §6.3, §6.6) y Cap. 7 |

El **objetivo general** (comparar, bajo un marco experimental común, estrategias de pronóstico en ocho regiones) corresponde al conjunto: el marco común se define en los capítulos 2 y 5, la comparación se realiza en el 6 y se interpreta en el 7.

## Parte B — Hallazgos de la revisión de la estructura (decisiones del autor)

| # | Observación | Detalle | Qué decidir |
|---|---|---|---|
| 1 | **El Cap. 3 no incluye STL.** | El índice del Cap. 3 solo trae fundamentos, estacionariedad, ARIMA y SARIMA; la descomposición STL se cita en el Cap. 1 y se usa en el 5, pero no se explica en un capítulo teórico. Afecta al O3. | Añadir una sección breve de STL al Cap. 3 (tendencia, estacionalidad y residuo; periodo de 168 h; versión robusta). |
| 2 | **El Cap. 4 repite el título "Deep Learning"** (§4.1.3 y §4.1.8). | Dos secciones con el mismo nombre. | Renombrar o fusionar. |
| 3 | **El Cap. 1 tiene una sola sección (§1.1 "Estado del arte")**, con el mismo nombre que el capítulo. | Los capítulos 1 y 2 no tienen subsecciones. | Opcional: subdividir. Relacionado con R7 (Roberto objeta la división por capítulos). |
| 4 | **Referencias [12] y [15] idénticas.** | Cerqueira, Torgo y Mozetič (2020) aparece dos veces en la bibliografía. | Eliminar una y unificar las citas (H25). |
| 5 | **El objetivo O5 pide "estabilidad", que hoy se apoya en una sola semana.** | El Cap. 6 actual compara en una semana (17–23 de mayo). La estabilidad entre semanas solo se puede mostrar con S1–S4. | Depende de los resultados en curso (ver R13, Parte E). |
| 6 | **R7 sigue abierta.** | Roberto pidió "no dividir la tesis por capítulos", pero no se sabe qué estructura espera. | Preguntarle antes de integrar esta sección; si la estructura cambia, el texto se reescribe. |
| 7 | **Dependencias entre correcciones.** | La sección describe el Cap. 2 con R14–R16 integrados y el Cap. 5 con R13 integrado. Si no se integran, la descripción no coincide con el contenido. | Integrar R12 al final, después de R13–R16. |

## Parte C — Coherencia con el alcance

La descripción del Cap. 2 usa la delimitación aprobada: el estudio incluye las siete regiones del Sistema Interconectado Nacional y el sistema de Baja California; Baja California Sur queda fuera como delimitación del alcance (no por falta de datos) y se menciona como trabajo futuro. Esto reemplaza la frase actual de §0.3.1 ("no se encontró una serie reciente de demanda para esa región"). Ver H16.
