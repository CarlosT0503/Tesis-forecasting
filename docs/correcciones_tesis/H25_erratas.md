# H25 — Erratas del PDF vigente (11) y propuestas de corrección

| Campo | Contenido |
|---|---|
| **Estado** | Redacción preparada (2026-10-22), con las decisiones del autor del 22/10 incorporadas (ver sección 4). **No integrada**: `tesis.tex` no se editó. |
| **Fuentes revisadas** | (1) Texto del PDF `…(11).pdf` (17/10). (2) Código fuente de la versión del **15/10** (`Series_de_Tiempo_para_la_Predicción_de_Consumo_Eléctrico (1).zip` en Descargas, `tesis.tex`), que es la más cercana al PDF (11); las líneas citadas abajo son de ese archivo. Se leyó, no se modificó ni se copió al repositorio. (3) El `tesis.tex` de Descargas del 24/09 **es una versión anterior** (sin Cap. 1 y con 8 referencias): solo se usó para recuperar el texto de una entrada bibliográfica. |
| **Alcance** | Erratas originales (a–d) y halladas en esta revisión (e–n). Ninguna toca resultados ni cifras experimentales. |
| **Límite** | El `.tex` del 15/10 puede no ser el último (el PDF es del 17/10). Antes de aplicar, confirmar que las líneas siguen siendo las mismas. |

## 1. Erratas originales

### (a) §5.1.1 — "nueve de las ocho regiones" (+ explicación de Baja California Sur)

`tesis.tex` (15/10), línea 1254. **Texto actual:** "Los experimentos modernos se realizaron de manera independiente para **nueve de las ocho** regiones del sistema eléctrico mexicano: … (PEN). Baja California Sur no se incluyó **edado** que no se encontró una serie de tiempo de demanda eléctrica reciente."

Defectos: el numeral, el error "edado" y la justificación, que se reemplazó por decisión del autor (H16): Baja California Sur queda fuera por delimitación del alcance, no por falta de datos. §0.3.1 (Introducción, línea 236 del `.tex`) usa la misma justificación y se corrige igual (R12, Parte C).

**Texto propuesto:**

> Los experimentos se realizaron de manera independiente para ocho series de demanda: las siete regiones de control del Sistema Interconectado Nacional —Central (CEN), Noreste (NES), Noroeste (NOR), Norte (NTE), Occidental (OCC), Oriental (ORI) y Peninsular (PEN)— y el sistema de Baja California (BCA). Baja California Sur queda fuera del alcance del estudio por delimitación y se plantea como trabajo futuro (sección 0.3).

"Modernos" se retira solo si el autor decide no conservar la distinción moderna/histórica (R13). Los nombres de región se unifican con los del Cap. 2 (punto g).

### (b) Bibliografía — [12] y [15] duplicadas, y una cita rota

**Cómo está implementada (verificado en el `.tex` del 15/10):** un entorno `thebibliography` escrito a mano, con claves simbólicas (`\bibitem{Cerqueira2020}`, `\cite{Cerqueira2020}`); **no hay archivo `.bib`**. En ese entorno **el número de cada referencia es su posición en la lista**, no su orden de aparición (por eso la Introducción cita primero [14], [3], [10]…). Dos consecuencias:

1. **La duplicación es literal:** las posiciones 12 y 15 son el mismo `\bibitem{Cerqueira2020}`, con la **misma clave**. LaTeX da la advertencia de etiqueta definida varias veces y todas las citas resuelven a la última (por eso el texto muestra solo [15]). La entrada 12 está **sin citar**.
2. **Borrar una entrada renumera automáticamente todas las posteriores** (las citas se actualizan solas), pero entonces [13]–[23] y las nuevas [24]–[35] cambiarían de número.

**Hallazgo nuevo que resuelve el dilema:** en el PDF (11), §4.1.6, aparece "propuesto por Chen y Guestrin **[?]**". El texto hace `\cite{XGBoost}` (línea 906 del `.tex`) pero **la entrada `\bibitem{XGBoost}` ya no existe** en la lista de 23 (sí existía en la versión del 24/09, donde decía: *Chen, T. & Guestrin, C. (2016): XGBoost: A Scalable Tree Boosting System. Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (KDD '16), ACM, Estados Unidos de América.*). Es una cita rota que hay que reparar de todos modos.

**Propuesta que conserva todos los números (decisión del autor del 22/10):** **sustituir la entrada duplicada y sin citar de la posición 12 por la de XGBoost.** Así:
- [12] pasa a ser Chen y Guestrin (2016) y `\cite{XGBoost}` deja de mostrar [?];
- [15] sigue siendo Cerqueira et al. (la que se cita), sin tocar ninguna cita;
- [1]–[11] y [13]–[23] no cambian, y las nuevas referencias siguen siendo [24]–[35] como en R14–R16. **No hace falta renumerar nada.**

Parche en `tesis.tex` (líneas 2147–2152 del `.tex` del 15/10; la primera de las dos entradas `Cerqueira2020`; la segunda, en 2171, no se toca):

```latex
\bibitem{XGBoost}
Chen, T. \& Guestrin, C. (2016):
\emph{XGBoost: A Scalable Tree Boosting System.}
Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (KDD '16),
ACM, Estados Unidos de América.
```

El texto de la entrada es el de la versión del 24/09 (del propio autor), con el formato de las demás entradas. **No añadí DOI ni páginas**: no los verifiqué en esta sesión; si se desean, hay que comprobarlos en la fuente. Antes de aplicarlo, confirmar que la posición 12 sigue siendo la primera `Cerqueira2020` en la versión vigente y que `LightGBM` sigue en [18].

### (c) Cap. 4 — dos secciones tituladas "Deep Learning" (§4.1.3 y §4.1.8)

**Decisión del autor (22/10): fusionar si el contenido es redundante, conservando toda la información técnicamente relevante.** Comparé ambas frase por frase:

| Contenido de §4.1.8 (PDF p. 19) | ¿Ya está en §4.1.3? |
|---|---|
| "Extensión de las redes neuronales artificiales tradicionales mediante múltiples capas ocultas… representaciones jerárquicas" | Sí (misma idea, otras palabras), salvo la caracterización "extensión de las redes tradicionales" |
| "Cada capa transforma progresivamente la información… patrones cada vez más complejos" | Sí ("la información es transformada progresivamente… características de mayor nivel de abstracción") |
| "Han demostrado un desempeño sobresaliente en tareas con relaciones altamente no lineales" | Parcial (§4.1.3 menciona "relaciones altamente no lineales" en su tercer párrafo, pero no el desempeño) |
| "En series de tiempo… relaciones estáticas y dependencias temporales de corto y largo plazo" | **No** — es lo único realmente nuevo |

Por tanto §4.1.8 es redundante salvo dos elementos, que se conservan en §4.1.3. **Texto fusionado** (§4.1.3 con lo que cambia en negritas; el resto de §4.1.3 queda como está):

> El *Deep Learning* es una rama del aprendizaje automático basada en redes neuronales artificiales con múltiples capas ocultas, diseñadas para aprender representaciones jerárquicas de los datos**; puede entenderse como una extensión de las redes neuronales artificiales tradicionales**. A diferencia de los modelos tradicionales de aprendizaje automático, donde las variables predictoras suelen definirse manualmente, … [sin cambios hasta el final del párrafo "El término *profundo*…"]
>
> **Las redes neuronales profundas han demostrado un desempeño sobresaliente en tareas donde existen relaciones altamente no lineales entre las variables. En el contexto del pronóstico de series de tiempo, estas arquitecturas permiten modelar tanto relaciones estáticas entre variables como dependencias temporales de corto y largo plazo.**
>
> En este trabajo se emplean dos arquitecturas de Deep Learning: … [sin cambios]

El párrafo en negritas es el segundo párrafo de §4.1.8 **verbatim**. No se pierde información.

**Parche en `tesis.tex` (15/10):**
1. En la subsección de la línea 871: añadir "; puede entenderse como una extensión de las redes neuronales artificiales tradicionales" al final de la primera oración, e insertar el párrafo anterior justo antes de "En este trabajo se emplean dos arquitecturas" (línea 885).
2. Eliminar la segunda `\subsection{Deep Learning}` completa (línea 1028 hasta antes de `\subsection{Entrenamiento mediante Gradiente}`, línea 1034).
3. Numeración resultante: §4.1.9→§4.1.8 (Entrenamiento mediante gradiente), §4.1.10→§4.1.9 (Perceptrón multicapa), §4.1.11→§4.1.10 (Modelo LSTM). **El `.tex` no tiene `\ref`/`\label` a estas subsecciones** (búsqueda de `\label{sec…}`: ninguna), así que no hay referencias cruzadas que romper; las ecuaciones del capítulo se numeran solas y §4.1.8 no tenía ecuaciones. Si el Cap. 5 o la Introducción del documento mencionan "sección 4.1.x" a mano, no encontré ninguna en el texto.

**Redundancias relacionadas** (no se tocan; decisión del autor, sin urgencia):
1. §4.1.4 "Entrenamiento de modelos supervisados" y §4.1.9 "Entrenamiento mediante gradiente" describen ambos la pérdida, el descenso del gradiente y la retropropagación.
2. $\hat y=f(x;\theta)$ aparece como (4.3) en §4.1.3 y de nuevo como (4.13) en §4.1.10.

### (d) Tabla 5.1 — filas desalineadas

**Lo que muestra la extracción de texto del PDF:** los valores aparecen desplazados una fila ("17–23 mayo 2026" frente a "Ventana de entrada", "168 horas" frente a "Entrenamiento", "336–3600 horas" frente a "Optimización", "Optuna" sin etiqueta). **Aviso:** sale de la extracción y de la nota previa de H25; no la revisé sobre la página renderizada y una extracción puede ordenar mal celdas que en el PDF sí están alineadas. Falta comprobar el entorno `tabular` de la Tabla 5.1 en el `.tex` (tampoco lo hice) o mirar la página.

**Tabla propuesta** (con la ventana adaptada a S1–S4, R13):

| Parámetro | Valor |
|---|---|
| Regiones | 8 (BCA, CEN, NES, NOR, NTE, OCC, ORI, PEN) |
| Frecuencia temporal | Horaria |
| Horizonte | 168 horas |
| Ventanas de prueba | cuatro semanas, S1–S4 (R13) |
| Ventana de entrada (DL, cuando aplica) | 168 horas |
| Entrenamiento | 336–3 600 horas, según familia |
| Optimización de hiperparámetros | Optuna (cuando aplica) |

Con el texto actual la fila de ventana valdría "17–23 de mayo de 2026".

## 2. Erratas halladas en esta revisión

| # | Ubicación | Texto actual | Corrección propuesta |
|---|---|---|---|
| e | Cap. 3, descomposición clásica (`.tex` líneas 654–657) | "El modelo clásico de descomposición **considere** tendencia y **estacionariedad**; se muestra en (1.3)." | "considera tendencia y **estacionalidad**". **Causa de "(1.3)":** la ecuación lleva `\tag{1.3}` escrito a mano (línea 657), la única `\tag` del documento; el contador no la numera. Quitar el `\tag{1.3}` para que se numere sola (saldría (3.x)) o cambiarlo a mano |
| f | §5.1.3 (`.tex` línea 1289) | "experimentos univariados**se** presenta" | "univariados se presenta" |
| g | §5.1.1 vs. Cap. 2 | Cap. 2: Occidental, Oriental, Peninsular; §5.1.1: Occidente, Oriente, Península de Yucatán | Unificar con los nombres del Cap. 2; verificar el nombre exacto en CENACE (R16) antes de fijarlo |
| h | §4.1.1 | Termina en "…es el aprendizaje supervisado" sin punto | Punto final (mejor, una frase que enlace con §4.1.2) |
| i | §4.1.7 | Dos citas "[18]" sin punto final | Punto tras la cita |
| j | Cap. 3, §3.1.1 | "…se muestra en la figura 3.1" sin punto final | Punto final |
| k | Bibliografía [19]–[22] | URLs escritas como texto plano (sin `\url{}`; `url` ya está cargado en el preámbulo, línea 17): la de [20] se corta en el margen y en [21] la `#` desaparece ("inicio//"); [22] "R. A (2016)" sin punto | Envolver en `\url{…}` ([19]–[21]); la URL correcta de [20] ya está completa en el `.tex` (`…/EnergiaGeneradaTipoTec.aspx`); [21]: `https://sie.energia.gob.mx/inicio/#/`. Ver también H23: [20] no respalda las series horarias |
| l | Cap. 2 | "El SIN se divide en nueve regiones operativas: BCA, BCS…" | Ya cubierta: R16 reemplaza la frase (H17). Contradice la lista de §5.1.1 |
| m | **§4.1.6 (cita rota)** | "Chen y Guestrin **[?]**" | Ver (b): restaurar la entrada de XGBoost en la posición 12 |
| n | **Referencias sin citar** | En el `.tex` (15/10), `Garcia` [19], `CENACE` [20] y `SIE` [21] no se citan en ninguna parte (las demás claves sí, y la de Cerqueira2020 está duplicada); la `Buitrago` está comentada | [20] y [21] las citarán R14–R16 (resuelto al integrar). **[19] Garcia (2019, blog de Xeridia)** sigue sin cita: citarla donde corresponda (p. ej., en la explicación de redes neuronales de §4.1) o retirarla. El autor decide. Además, una referencia a un blog es débil frente a las demás |

## 3. Efecto sobre otras correcciones

| Corrección de H25 | Toca a |
|---|---|
| (a) | R12 Parte C (§0.3.1), R13 Parte C (puntos 1–2), R16 §2.5 |
| (b) | **Nada**: la numeración [24]–[35] de R14–R16/H23 se conserva |
| (c) | R12 Parte B (hallazgo 2); la descripción del Cap. 4 de §0.4 no cita numeración, por lo que no cambia |
| (d) | R13 (matriz experimental y ventanas S1–S4) |
| (e) | Subsección STL (`C3_subseccion_STL.md`), que numera su ecuación nueva (3.7) |

## 4. Decisiones del autor del 22/10 que recoge este documento

1. Conservar los números de referencia existentes, sin renumeración general → resuelto con la sustitución de la entrada 12 (b). La verificación que se pidió está hecha: bibliografía manual (`thebibliography`) con numeración posicional.
2. Fusionar §4.1.3 y §4.1.8 si es redundante, conservando lo técnicamente relevante → (c).
3. `tesis.tex` sin editar todavía.

## 5. Pendiente

1. Confirmar que el `.tex` del 15/10 es el vigente (o compartir el último) antes de aplicar los parches.
2. Decisión del autor: qué hacer con [19] Garcia (n); si se mantiene "modernos" en §5.1.1; si se añaden DOI/páginas a XGBoost tras verificarlos.
3. Comprobar la Tabla 5.1 (d) sobre la página o el `.tex`.
