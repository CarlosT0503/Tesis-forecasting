# Seguimiento de las 23 observaciones de Roberto

Estados: **Pendiente** · **En preparación** · **Redacción preparada** · **Integrada en tesis** · **Verificada**.

- *Integrada en tesis* = el cambio ya está en el PDF vigente (`Series_de_Tiempo_para_la_Predicción_de_Consumo_Eléctrico (11).pdf`, idéntico al (10)).
- *Verificada* = Roberto (o el autor) confirmó que la observación quedó resuelta. **Ninguna lo está todavía.**
- Las correcciones preparadas viven en archivos independientes de esta carpeta; **`tesis.tex` y el PDF no se han tocado.**

Última actualización: 2026-10-20. Hallazgos que afectan a varias observaciones: ver `HALLAZGOS_PENDIENTES.md` (H1–H26).

| # | Observación (resumen) | Categoría | Tipo | Estado | Archivo / evidencia | Notas y dependencias |
|---|---|---|---|---|---|---|
| R1 | Cambiar formato de la carátula | Estructura | Cambio | Integrada en tesis | PDF p. 1 (logo BUAP, nombre, asesores, fecha) | Falta que Roberto confirme el formato. La fecha dice "Agosto 2026". |
| R2 | Mejorar idea de combustibles fósiles / párrafos por idea | Redacción | Cambio | Integrada en tesis | PDF pp. xi–xii (introducción reescrita; el párrafo ya no existe) | Reemplazada, no corregida. |
| R3 | "Casi todas las actividades humanas" (energía) | Redacción | Cambio | Integrada en tesis | PDF: la frase ya no aparece | Idem. |
| R4 | Puente fósiles → planeación, ~2 páginas | Justificación | Cambio | Integrada en tesis | PDF pp. xi–xii | Roberto debe aceptar el enfoque nuevo (sin hilo energético/ambiental). |
| R5 | Justificación: utilidad, problemas, por qué no es simple | Justificación | Cambio | Pendiente (parcial) | PDF pp. xi–xii cubren utilidad operativa y dificultad | Falta beneficio concreto de predecir en México. |
| R6 | Estadísticas y citas en la justificación | Justificación | Sugerencia | Pendiente (parcial) | Citas sí; cifras no | Opcional. |
| R7 | No dividir la tesis por capítulos | Estructura | Ambigua | Pendiente | 7 capítulos de 2 a 10 páginas | Preguntar a Roberto qué estructura espera. |
| R8 | "¿Cuál fue el primero?" (LightGBM) | Estructura / metodología | Pregunta | Pendiente | PDF p. 33 | Se resuelve con R23. |
| R9 | Looker Studio "no va aquí" | Estructura | Cambio | Pendiente | PDF p. 34 | Decidir dónde va (o quitarlo). |
| R10 | ¿Era realmente el objetivo? | Objetivos | Pregunta | Pendiente (parcial) | PDF p. xii (objetivo general), p. 41 | Falta mapear conclusiones a los 5 objetivos específicos. |
| R11 | Antecedentes: revisión extensa | Antecedentes | Cambio | Integrada en tesis | PDF Cap. 1, pp. 1–4 | Roberto decide si basta con 4 páginas. |
| R12 | Estructura del trabajo y objetivos | Objetivos / estructura | Cambio | **Redacción preparada** | `R12_estructura_tesis.md` | Nueva §0.4 con los 7 capítulos reales (PDF vigente) y tabla objetivos–capítulos. Depende de integrar R13–R16 y de R7 (estructura que espera Roberto). Hallazgos: el Cap. 3 no explica STL (afecta O3); "Deep Learning" repetido en el Cap. 4; refs. [12]=[15] (H25). |
| R13 | Metodología general (pasos del trabajo) | Metodología | Cambio | **Redacción preparada** | `R13_metodologia_general.md` | Describe el diseño definitivo (S1–S4) en 7 pasos; distingue experimentos anteriores; lista limitaciones (H3, H7, H8, H14, H24). Contrasta con el texto actual del Cap. 5 ("nueve de las ocho regiones", BCS, BCA 384 h). Los resultados de los Caps. 6–7 dependen de que terminen las 216 corridas. |
| **R14** | **Fuentes de los datos, cobertura, procesamiento** | Metodología / antecedentes | Cambio | **Redacción preparada** | `R14_cierre_procedencia_y_procesamiento.md` (definitivo), `R14_fuentes_datos.md/.tex` (exógenas) | H14 y H15 resueltos. Pendiente real: script original de construcción no localizado (procedimiento descrito como reproducible, no recuperado). Inserción: nueva §2.1. |
| R15 | Qué es generación y qué es consumo | Antecedentes | Cambio | **Redacción preparada** | `R15_generacion_consumo_demanda.md` | Incluye ecuación del balance verificada numéricamente. Decidir 'consumo' vs 'demanda' en el título. Inserción: nueva §2.2. |
| R16 | Contexto de México (plantas, origen, importaciones) | Antecedentes | Cambio | **Redacción preparada** | `R16_contexto_sistema_electrico.md` | **Versión 2 ampliada (2026-10-19):** conecta las Figs. 2.1–2.5 en una narrativa (§2.4), cifras recalculadas, tablas regional 2023 y patrones; refs [26]–[32] con \bibitem. Capacidad 93 788 MW verificada (PRODESEN). INEGI aportado por el autor, no reverificado. **Figs. 2.1, 2.2, 2.4 y 2.5 regeneradas (2026-10-20) en `figuras_cap2/`, pendientes de revisión del autor; Fig. 2.3 sin regenerar. BCS redactada como delimitación del alcance (H16).** Inserción: §2.3–§2.6. |
| R17 | Por qué importan las series de tiempo | Justificación | Cambio | Pendiente | PDF p. 9 | — |
| R18 | Diferencia ML/DL respecto a lo anterior | Justificación | Cambio | Pendiente | PDF p. 15 | — |
| R19 | "Metodología" → "Experimentación" | Estructura | Cambio | Pendiente | PDF p. 25 | Ajustar referencias cruzadas. |
| R20 | Explicar mejor por qué gana Naive+T+S | Resultados | Cambio | Pendiente | PDF p. 27 | Datos S1–S4 (extensión) pueden apoyar la explicación. |
| R21 | Resumen ARIMA / SARIMA / Naive+T+S con tabla y gráfica | Resultados | Cambio | Pendiente | PDF pp. 29–30 | Decidir comparabilidad de ventanas; los resultados S1–S4 pueden alimentarlo. |
| R22 | LSTM: resumir y explicar qué pudo pasar | Resultados | Cambio | Pendiente | PDF pp. 31–32 | Bloqueada por la procedencia de `tab:lstm_resultados` (script legacy perdido). |
| R23 | XGBoost y ensamble propuesto | Metodología / alcance | Mixto | Pendiente | PDF p. 33 | Ambigua: ¿presentar XGBoost, o ensamble nuevo? Preguntar a Roberto. |

## Resumen

| Estado | Cantidad |
|---|---|
| Redacción preparada | 5 (R12, R13, R14, R15, R16) |
| Integrada en tesis (sin verificar con Roberto) | 5 (R1–R4, R11) |
| Pendiente (parcial) | 3 (R5, R6, R10) |
| Pendiente | 10 (R7, R8, R9, R17–R23) |
| En preparación | 0 |
| Verificada | 0 |

## Registro de cambios de este archivo

- 2026-10-17: creación; R14 pasa a *Redacción preparada*.
- 2026-10-19: R16 reescrito (versión 2) y vinculado a las Figs. 2.1–2.5; hallazgos H19–H23.
- 2026-10-18: R14 cerrado (BCA, liquidaciones, procesamiento); R15 y R16 pasan a *Redacción preparada*. Resumen: `RESUMEN_CIERRE_R14_R15_R16.md`.
- 2026-10-20: R12 y R13 pasan a *Redacción preparada*; R14/R16 corregidos con la delimitación de alcance de Baja California Sur (H16); figuras 2.1, 2.2, 2.4 y 2.5 regeneradas; revisión de consistencia de R15; hallazgos H24 (XGBoost sin tuning efectivo), H25 (erratas) y H26 (cobertura del consumo SIE).
