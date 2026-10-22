# H25 — Erratas del PDF vigente (11) y propuestas de corrección

| Campo | Contenido |
|---|---|
| **Estado** | Redacción preparada (2026-10-22). **No integrada** en `tesis.tex`. |
| **Método** | Texto extraído del PDF vigente `…(11).pdf`; cada hallazgo se contrastó con el texto circundante y, para las referencias, con todas las citas del documento. Las páginas son las del índice del PDF. |
| **Alcance** | Cuatro erratas originales (a–d) más las halladas en esta revisión (e–l). Ninguna toca resultados ni cifras experimentales. |
| **Pendiente de visto bueno** | Decisión sobre la bibliografía (b) y sobre la fusión de §4.1.3/§4.1.8 (c). El resto son correcciones directas. |

## 1. Erratas originales

### (a) §5.1.1, p. 25 — "nueve de las ocho regiones" (+ explicación de Baja California Sur)

**Texto actual:** "Los experimentos modernos se realizaron de manera independiente para **nueve de las ocho** regiones del sistema eléctrico mexicano: … (PEN). Baja California Sur no se incluyó **edado** que no se encontró una serie de tiempo de demanda eléctrica reciente."

Hay tres defectos en dos frases: el numeral ("nueve de las ocho"), el error tipográfico "edado" y, sobre todo, una justificación que se reemplazó por decisión del autor (H16): Baja California Sur queda fuera por delimitación del alcance, no por falta de datos. La frase de §0.3.1 (Introducción) tiene la misma justificación y se corrige igual (R12, Parte C).

**Texto propuesto:**

> Los experimentos se realizaron de manera independiente para ocho series de demanda: las siete regiones de control del Sistema Interconectado Nacional —Central (CEN), Noreste (NES), Noroeste (NOR), Norte (NTE), Occidental (OCC), Oriental (ORI) y Peninsular (PEN)— y el sistema de Baja California (BCA). Baja California Sur queda fuera del alcance del estudio por delimitación y se plantea como trabajo futuro (sección 0.3).

Cambios respecto al original: "ocho series" en lugar de "nueve de las ocho regiones"; se retira "modernos" **solo si** el autor decide no conservar la distinción moderna/histórica (ver R13); y se unifican los nombres (punto g).

### (b) Bibliografía — [12] y [15] idénticas

**Verificado:** las entradas [12] y [15] son la misma obra (Cerqueira, Torgo y Mozetič, 2020, *Machine Learning* 109, 1997–2028, DOI 10.1007/s10994-020-05910-7). En el texto **solo se cita [15]** (una vez en la Introducción y dos en el Cap. 1, en la revisión sobre estimación del desempeño). **[12] no se cita en ninguna parte** (búsqueda de "[12]" en todo el texto extraído: solo aparece en la propia bibliografía).

Esto simplifica la corrección: no hay que unificar citas, solo retirar una entrada. Pero la numeración de la bibliografía **no sigue el orden de aparición** (la Introducción cita primero [14], [3], [10], [13]), por lo que parece manual: al borrar una entrada hay que decidir qué pasa con los números.

| Opción | Qué se hace | Efecto |
|---|---|---|
| **A (recomendada, menor impacto)** | Se elimina la entrada [15] y las 3 citas "[15]" pasan a "[12]". Queda un hueco en [15]; se rellena moviendo allí la referencia nueva con número más alto (la propuesta [35] pasa a [15]). | Ninguna cita existente cambia salvo las 3 de Cerqueira. En los borradores R14–R16 hay que sustituir "[35]" por "[15]". Sin hueco ni renumeración en cadena |
| B | Se elimina [12]; [13]–[23] bajan una posición; las nuevas [24]–[35] pasan a [23]–[34] | Cambia ~18 citas del texto y todas las de R14–R16 (69 apariciones de [24]–[35] en los borradores). Más limpio si la bibliografía es automática (BibTeX), más trabajo si es manual |
| C | No hacer nada | Se queda una referencia duplicada y huérfana; Roberto la verá |

**Decisión del autor:** A o B. Si `tesis.tex` usa BibTeX con orden por aparición, B es automático y no hay nada que hacer a mano; `tesis.tex` no está en este repositorio, no pude comprobarlo. Hasta decidir, **los borradores mantienen sus números provisionales**.

### (c) Cap. 4 — dos secciones tituladas "Deep Learning" (§4.1.3 y §4.1.8)

**Lo que dicen:**
- §4.1.3 (p. 16): define Deep Learning, introduce $\hat y=f(x;\theta)$ (4.3), explica "profundo" y anuncia las dos arquitecturas usadas (MLP y LSTM).
- §4.1.8 (p. 19): dos párrafos que repiten la idea (múltiples capas ocultas, representaciones jerárquicas) y añaden solo que las redes profundas modelan relaciones no lineales y, en series de tiempo, dependencias estáticas y temporales de corto y largo plazo.

**Diagnóstico:** §4.1.8 no aporta definición nueva; su única contribución es la frase sobre series de tiempo. Además, el capítulo interpone entre ambas el entrenamiento supervisado (§4.1.4) y el gradient boosting (§4.1.5–§4.1.7), de modo que el lector encuentra la definición de DL, la deja, y la reencuentra.

**Propuesta (recomendada): fusionar.** Conservar §4.1.3 y añadirle al final el párrafo único de §4.1.8, redactado así:

> Las redes neuronales profundas han demostrado un desempeño sobresaliente en tareas con relaciones altamente no lineales entre las variables. En el pronóstico de series de tiempo permiten modelar tanto relaciones estáticas entre variables como dependencias temporales de corto y largo plazo.

Después se elimina §4.1.8 y las secciones siguientes se renumeran: §4.1.9→§4.1.8 (Entrenamiento mediante gradiente), §4.1.10→§4.1.9 (Perceptrón multicapa), §4.1.11→§4.1.10 (Modelo LSTM). No hay ecuación en §4.1.8, por lo que la numeración de ecuaciones no cambia. **No encontré referencias cruzadas a esas secciones** en el texto extraído (búsqueda de "sección 4.x"), pero conviene buscar `\ref` en `tesis.tex`.

Alternativa mínima (si se prefiere no mover texto): renombrar §4.1.8 a "Redes neuronales profundas para series de tiempo" y quitar de ella las dos frases ya dichas en §4.1.3. Es menos limpia: sigue habiendo dos introducciones al mismo concepto.

**Redundancias relacionadas** (decisión del autor; no son errores):
1. §4.1.4 "Entrenamiento de modelos supervisados" y §4.1.9 "Entrenamiento mediante gradiente" describen ambos la pérdida, el descenso del gradiente y la retropropagación. Se podría dejar el detalle matemático solo en §4.1.9 y reducir §4.1.4 a lo general (mismo mecanismo para cualquier modelo supervisado).
2. $\hat y=f(x;\theta)$ aparece como (4.3) en §4.1.3 y de nuevo como (4.13) en §4.1.10.

### (d) Tabla 5.1, p. 26 — filas desalineadas

**Lo que muestra la extracción de texto:**

| Fila | Valor aparente |
|---|---|
| Ventana de prueba principal | (vacío) |
| Ventana de entrada (DL, cuando aplica) | 17–23 mayo 2026 |
| Entrenamiento | 168 horas |
| Optimización | (vacío) …y luego "336–3600 horas, según familia", "Optuna (cuando aplica)" |

Los valores parecen desplazados una fila respecto de sus etiquetas: "17–23 mayo 2026" pertenece a la ventana de prueba, "168 horas" a la ventana de entrada, "336–3600 horas" al entrenamiento y "Optuna" a la optimización. **Aviso:** esta lectura sale de la extracción de texto y de la nota previa de H25; **no la revisé visualmente en esta sesión** sobre la página renderizada, y una extracción puede ordenar mal celdas que en el PDF sí están alineadas. Confirmarlo mirando la página antes de corregir.

**Tabla propuesta** (con la ventana ya adaptada a S1–S4, según R13):

| Parámetro | Valor |
|---|---|
| Regiones | 8 (BCA, CEN, NES, NOR, NTE, OCC, ORI, PEN) |
| Frecuencia temporal | Horaria |
| Horizonte | 168 horas |
| Ventanas de prueba | cuatro semanas, S1–S4 (R13) |
| Ventana de entrada (DL, cuando aplica) | 168 horas |
| Entrenamiento | 336–3 600 horas, según familia |
| Optimización de hiperparámetros | Optuna (cuando aplica) |

La fila "Ventana de prueba" se sustituye cuando se integre R13; con el texto actual valdría "17–23 de mayo de 2026".

## 2. Erratas halladas en esta revisión

| # | Ubicación | Texto actual | Corrección propuesta |
|---|---|---|---|
| e | Cap. 3 (descomposición clásica) | "El modelo clásico de descomposición **considere** tendencia y **estacionariedad**; se muestra en (1.3)." | "considera tendencia y **estacionalidad**; se muestra en (3.3)." (concordancia; el concepto correcto es estacionalidad —la estacionariedad es otra cosa, §3.1.3—; y la ecuación está en el Cap. 3, no en el 1). Verificar el número real de la ecuación con `\label` |
| f | §5.1.3, p. 26 | "experimentos univariados**se** presenta" (falta espacio) | "experimentos univariados se presenta" |
| g | §5.1.1 vs. Cap. 2 | Cap. 2: "Occidental (OCC), Oriental (ORI), Peninsular (PEN)"; §5.1.1: "Occidente (OCC), Oriente (ORI), Península de Yucatán (PEN)" | Unificar con los nombres del Cap. 2 (Occidental, Oriental, Peninsular), que son los de las regiones de control; verificar el nombre exacto en la fuente de CENACE (R16) antes de fijarlo |
| h | §4.1.1, p. 15 | Termina en "Una rama del aprendizaje automático es el aprendizaje supervisado" sin punto | Añadir el punto final (y, mejor, una frase que enlace con §4.1.2) |
| i | §4.1.7, pp. 18–19 | Dos citas "[18]" sin punto final ("…del árbol [18]") | Punto tras la cita |
| j | Cap. 3, §3.1.1 | "…se muestra en la figura 3.1" sin punto final | Punto final |
| k | Bibliografía | [19] usa "(2019)." (formato distinto a las demás); [20] termina sin punto y con la dirección cortada ("…/Energia"); [21] termina en "//."; [22] "R. A (2016)" sin punto tras la inicial | Unificar formato; la [20] y la [21] merecen revisión: ver R14/R16 y H23 (la [20] no respalda las series horarias de demanda) |
| l | Cap. 2, p. 7 | "El Sistema Interconectado Nacional (SIN) se divide en nueve regiones operativas: Baja California (BCA), Baja California Sur (BCS)…" | Ya está cubierta: R16 reemplaza esa frase (H17). La dejo anotada aquí porque contradice la lista de §5.1.1, que separa las siete regiones del SIN de BCA |

## 3. Efecto sobre otras correcciones

| Corrección de H25 | Toca a |
|---|---|
| (a) | R12 Parte C (§0.3.1), R13 Parte C (puntos 1–2), R16 §2.5 |
| (b) | Numeración de referencias de R14, R15, R16 y H23 |
| (c) | R12 Parte B (hallazgo 2) y descripción del Cap. 4 en §0.4 (el texto de R12 no cita numeración de subsecciones, por lo que no cambia) |
| (d) | R13 (matriz experimental y ventanas S1–S4) |
| (e) | Subsección STL (C3), que cita la misma ecuación |

## 4. Lo que necesito del autor

1. Bibliografía: opción A o B para [12]/[15] (y si la bibliografía es automática).
2. §4.1.3/§4.1.8: ¿fusión (recomendada) o renombre?
3. Confirmar (d) mirando la página 26 del PDF (o `tesis.tex`).
4. ¿Se retira "modernos" en §5.1.1 (R13)?
