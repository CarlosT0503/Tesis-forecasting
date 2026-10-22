# H26 — Revisión: ¿se confunden las ventas del suministro básico con el consumo total del SEN?

Fecha: 2026-10-22. Alcance: PDF vigente (11) de la tesis y los borradores R12–R16. Método: búsqueda de todas las apariciones de "consumo" (19 en el PDF) y lectura de su contexto. Referencia: `H26_discrepancia_SIE_SENER.md`.

## 1. Resultado en una línea

La confusión está **confinada al Capítulo 2** (texto y títulos de las Figuras 2.1, 2.2 y 2.5). **Los objetivos, la metodología, los resultados y las conclusiones no la contienen**, porque la variable que se pronostica es la *demanda* horaria por balance de CENACE, no la serie anual del SIE; la serie del SIE no interviene en ningún experimento.

## 2. Tesis (PDF vigente)

| Ubicación | Texto actual (resumen) | ¿Confunde SSB con consumo total? | Acción propuesta |
|---|---|---|---|
| Título y portada | "…predicción de **Consumo** Eléctrico" | No es un error de datos; la variable pronosticada es la demanda, y el texto de §0.3.1 ya dice "se utiliza el término demanda eléctrica". Es un tema de **nomenclatura** | **Decisión del autor** (R15): se deja intacto hasta consultarlo |
| Índice de figuras | 2.1 "Consumo eléctrico promedio por entidad federativa"; 2.2 "Consumo eléctrico total en México"; 2.5 "Consumo vs. generación eléctrica promedio" | **Sí**: 2.2 dice "total" y la serie son ventas de CFE SSB | Nuevos títulos (ya aplicados en `figuras_cap2/`): "Ventas anuales promedio de electricidad de CFE Suministro Básico por entidad federativa", "Ventas de electricidad de CFE Suministro Básico, total nacional" y "Ventas de CFE Suministro Básico y generación bruta (CFE + PIE) por entidad federativa" |
| Cap. 2, p. 5 | "La Figura 2.1 presenta el consumo eléctrico promedio por entidad…"; "mayores niveles promedio de consumo eléctrico" | **Sí** (mismo motivo) | Reescribir con "ventas" y la nota de cobertura: R16 §2.4 |
| Cap. 2, p. 5 | "La Figura 2.2 muestra el consumo eléctrico anual total en México. Se observa… una reducción en el año 2024" | **Sí** ("total") y además la "reducción" es un artefacto de datos parciales (H20) | R16 §2.4: ventas de CFE SSB; 2024 parcial; dato anual publicado de 2024 = 225 213 GWh (+1.0 %) |
| Cap. 2, p. 7 | Figura 2.5: "diferencias amplias entre generación y consumo promedio, como Veracruz y Jalisco… equilibrado… Oaxaca y San Luis Potosí" | **Sí**, y el ejemplo es incorrecto (H21: San Luis Potosí genera 1.7 veces sus ventas; los equilibrados son Oaxaca, Baja California Sur y Campeche) | R16 §2.4 |
| Introducción, p. xi | "la generación debe mantenerse en equilibrio con el consumo" | No: es una afirmación general de operación del sistema, no un dato | Sin cambio |
| Cap. 1, p. 1 y p. 3 | "comportamiento del consumo"; "datos de consumo de Francia metropolitana" (literatura) | No | Sin cambio |
| Cap. 3, §3.1.1 | "el consumo eléctrico, en verano" (ejemplo de estacionalidad) | No: ejemplo ilustrativo | Sin cambio |
| Cap. 4 | "consumo de memoria" | No: no es consumo eléctrico | Sin cambio |
| Objetivos y alcance (§0.2–§0.3) | "demanda eléctrica"; las ocho series de CENACE | No | Sin cambio |
| Metodología, Resultados, Conclusiones (Caps. 5–7) | "demanda"; ninguna mención de "consumo" eléctrico | No | Sin cambio |

## 3. Borradores (R12–R16)

| Borrador | Estado | Acción |
|---|---|---|
| R12 (§0.4, Cap. 2) | La frase "diferencia entre generación, consumo y demanda" es correcta | Añadida la aclaración sobre la cobertura de la serie por entidad del SIE |
| R13 (metodología) | No usa la serie del SIE; la variable es la demanda | Sin cambio |
| R14 (fuentes) | Describía la serie como "consumo" y la limitación (iii) igual | Corregido (.md y .tex): denominación "ventas de CFE Suministro Básico (rotulada «consumo» por el SIE)", cita [33], identificación como inferencia; nota de 2024 actualizada con la cifra publicada |
| R15 (definiciones) | Las definiciones de consumo final, bruto y demanda son de SENER/CENACE y son correctas | Añadido el párrafo "La serie anual por entidad del SIE" |
| R16 (contexto) | §2.4 y la Parte A llamaban "consumo" a esa serie (56 menciones) | Reescrita §2.4, tablas de las figuras y referencias; quedan 15 menciones, todas legítimas (consumo final/bruto de SENER, título oficial de la tabla del SIE, descripciones de la fuente) |

## 4. Interpretación de las figuras

- **Figuras 2.1, 2.2 y 2.5:** representan las ventas de CFE Suministro Básico (inferido, H26). Cada una lleva en el pie la nota de que la identificación se verificó para 2019–2023 y de que antes de 2019 se **asume** la misma definición.
- **Figura 2.3 (generación anual) y 2.4 (generación por entidad):** son generación bruta de CFE + PIE; no cambian de denominación.
- **Lectura correcta del conjunto:** las cinco figuras son contexto descriptivo; no sustentan ninguna conclusión de la tesis.

## 5. Decisiones del autor (22/10) y puntos de aplicación

**Terminología aprobada:**
1. **Objetivo y variable pronosticada: «demanda eléctrica».** Es lo que ya dicen la Introducción y los Caps. 5–7; no requiere cambios.
2. **Figuras basadas en el SIE: «ventas de electricidad de CFE Suministro Básico»**, aclarando en el texto y en el pie que **no representan el consumo final total del SEN** (nota ya incluida en las figuras regeneradas y en R16 §2.4).
3. **El título de la tesis no se cambia** hasta revisar su formulación exacta (abajo).

**Formulación exacta del título** (`tesis.tex`, versión del 15/10, línea 34): `\title{Series de Tiempo para la predicción de Consumo Eléctrico}`; el nombre del PDF repite "Predicción de Consumo Eléctrico". El texto de la tesis usa "demanda eléctrica" para lo que se pronostica (Introducción: líneas 71, 118, 129, 171, 178 del `.tex`). Hay una incongruencia entre el título ("consumo") y la variable ("demanda"), pero **no se modifica**: es una decisión del autor/asesores, que puede implicar trámites (portada, registro, resúmenes, pósteres, protocolo). Si se decidiera cambiarlo, la forma mínima sería «…Predicción de **Demanda** Eléctrica», pero no se propone aplicarla.

**Puntos del `.tex` (15/10) que cambian con la decisión 2** (no aplicados; `tesis.tex` no se edita):

| Línea | Hoy | Cambio propuesto |
|---|---|---|
| 575 | `\caption{Consumo eléctrico promedio por entidad federativa}` | Ventas anuales promedio de electricidad de CFE Suministro Básico por entidad federativa |
| 579 | "La Figura … muestra el consumo eléctrico anual total en México. Se observa una disminución…" | R16 §2.4 (ventas de CFE SSB; 2024 parcial; no es una caída) |
| 584 | `\caption{Consumo eléctrico total en México}` | Ventas de electricidad de CFE Suministro Básico, total nacional |
| 604 | "…diferencias amplias entre generación y consumo promedio, como Veracruz y Jalisco…" | R16 §2.4 (ventas; ejemplos corregidos, H21) |
| 609 | `\caption{Consumo vs. generación eléctrica promedio}` | Ventas de CFE Suministro Básico y generación bruta (CFE + PIE) por entidad federativa |
| 574, 583, 608 | Archivos `img/Consumo Promedio.png`, `img/Consumo Anual.png`, `img/Consumo vs Generacion.png` | Sustituir por los PNG regenerados en `figuras_cap2/` (`Fig2_1_Ventas_CFE_SSB_por_entidad.png`, `Fig2_2_Ventas_CFE_SSB_nacional.png`, `Fig2_5_Ventas_SSB_vs_Generacion.png`); actualizar los `\includegraphics` |

El resto de las 18 apariciones de "consumo" en el `.tex` son usos legítimos (ver sección 2).

## 6. Lo que sigue abierto

1. Si, además de renombrar las figuras, se conserva la palabra "consumo" en el texto corrido del Cap. 2: R16 usa "ventas" y explica la equivalencia una vez; con las decisiones 1 y 2 esto es coherente.
2. El título (decisión 3).
