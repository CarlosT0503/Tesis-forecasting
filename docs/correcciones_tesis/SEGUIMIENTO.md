# Seguimiento de las 23 observaciones de Roberto

Estados: **Pendiente** · **En preparación** · **Redacción preparada** · **Integrada en tesis** · **Verificada**.

- *Integrada en tesis* = el cambio ya está en el PDF vigente (`Series_de_Tiempo_para_la_Predicción_de_Consumo_Eléctrico (11).pdf`, idéntico al (10)).
- *Verificada* = Roberto (o el autor) confirmó que la observación quedó resuelta. **Ninguna lo está todavía.**
- Las correcciones preparadas viven en archivos independientes de esta carpeta; **`tesis.tex` y el PDF no se han tocado.**

Última actualización: 2026-10-17.

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
| R12 | Estructura del trabajo y objetivos | Objetivos / estructura | Cambio | Pendiente (parcial) | Objetivos pp. xii–xiii; falta la descripción de capítulos | Escribir al final. |
| R13 | Metodología general (pasos del trabajo) | Metodología | Cambio | Pendiente | — | Escribir al final. |
| **R14** | **Fuentes de los datos, cobertura, limitaciones** | Metodología / antecedentes | Cambio | **Redacción preparada** | `R14_fuentes_datos.md` / `.tex` | Pendientes de verificar al pie del archivo (fuente de temperatura, ref. INEGI, MD5 en Drive, Imp/Exp, periodo del Cap. 2, 2024 incompleto). Inserción propuesta: nueva §2.1. |
| R15 | Qué es generación y qué es consumo | Antecedentes | Cambio | Pendiente | — | No adelantada. Depende de R14 y del término "demanda/consumo". |
| R16 | Contexto de México (plantas, origen, importaciones) | Antecedentes | Cambio | Pendiente | — | No adelantada. |
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
| Redacción preparada | 1 (R14) |
| Integrada en tesis (sin verificar con Roberto) | 5 (R1–R4, R11) |
| Pendiente (parcial) | 4 (R5, R6, R10, R12) |
| Pendiente | 13 |
| En preparación | 0 |
| Verificada | 0 |

## Registro de cambios de este archivo

- 2026-10-17: creación; R14 pasa a *Redacción preparada*.
