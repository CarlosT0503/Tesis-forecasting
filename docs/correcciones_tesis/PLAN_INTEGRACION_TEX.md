# Plan ordenado para integrar las correcciones al `tesis.tex`

Preparado el 2026-10-22. **No se ha editado ningún `.tex`.** Este plan se ejecuta solo cuando el autor confirme la versión vigente y autorice expresamente cada fase.

## 0. Puerta de entrada: confirmar la versión vigente

Referencia provisional (decisión del autor, 22/10): el `tesis.tex` del **15/10** (dentro de `Series_de_Tiempo_para_la_Predicción_de_Consumo_Eléctrico (1).zip`, Descargas; 124 KB, 2 210 líneas). Es la más cercana al PDF (11) del 17/10, pero **no está confirmada como la última**: hay dos `.tex` más en Descargas (24/09 y 23/08) y el proyecto de Overleaf puede tener cambios posteriores al 15/10.

| Comprobación | Cómo | Resultado esperado |
|---|---|---|
| Versión | El autor exporta de nuevo el proyecto de Overleaf (o confirma que el zip del 15/10 es el último) y se compara con el del 15/10 (`diff`) | Sin diferencias, o diferencias listadas |
| Coincide con el PDF (11) | Mismos títulos de sección y mismos defectos: "nueve de las ocho", `Chen y Guestrin [?]`, dos `\subsection{Deep Learning}`, `\tag{1.3}` | Los cuatro presentes |
| Líneas de los parches | Los números de línea de `H25_erratas.md` y `H26_revision_uso_de_consumo.md` son del `.tex` del 15/10 | Si el archivo cambió, se recalculan buscando el texto, no el número |
| Compilación base | Compilar el `.tex` sin cambios y guardar el PDF y el `.log` como línea base (advertencias de etiquetas duplicadas, citas indefinidas) | PDF idéntico al (11) y lista de advertencias conocida (incluye `Cerqueira2020` duplicada y `XGBoost` indefinida) |

**Reglas de trabajo para toda la integración:** trabajar sobre una **copia** (`tesis_integracion.tex`), nunca sobre el original; una fase por vez, con compilación después de cada una; un commit/respaldo por fase; el original solo se reemplaza cuando el autor lo apruebe.

## 1. Orden de fases (de menor a mayor riesgo y dependencia)

Cada fase indica el documento fuente, qué se toca y cómo se verifica. Las fases con **[decisión]** necesitan respuesta previa del autor.

### Fase 1 — Erratas mecánicas (riesgo bajo, sin cambio de contenido)
Fuente: `H25_erratas.md`, secciones 1 y 2.

| Cambio | Detalle |
|---|---|
| "nueve de las ocho" y "edado" en §5.1.1; justificación de BCS | Texto propuesto en H25 (a); misma justificación en §0.3.1 (R12 Parte C) |
| "considere … estacionariedad" → "considera … estacionalidad" | H25 (e) |
| `\tag{1.3}` en la descomposición clásica | Quitar la `\tag` (se numera sola) o ponerla a mano; revisar que `\eqref{eq:clasicodescomp}` siga funcionando |
| "univariadosse", puntos finales faltantes (§4.1.1, §4.1.7, §3.1.1) | H25 (f), (h), (i), (j) |
| Nombres de región (Occidental, Oriental, Peninsular) | H25 (g); **verificar el nombre exacto en CENACE** antes |

Verificación: compilar; comparar el PDF con la línea base (solo deben cambiar esas líneas).

### Fase 2 — Bibliografía sin renumerar
Fuente: `H25_erratas.md` (b), (k), (n). **No cambia ningún número.**

1. Sustituir el **primer** `\bibitem{Cerqueira2020}` (posición 12) por `\bibitem{XGBoost}` con los datos verificados (DOI, KDD '16, San Francisco; páginas 785–794 pendientes de confirmar en ACM). Resultado esperado: desaparece `Chen y Guestrin [?]`, la cita sale como [12] y [15] sigue siendo Cerqueira.
2. Envolver las URL de [19]–[21] en `\url{…}` (el paquete `url` ya está cargado).
3. **[19] Garcia: no tocar** (retiro solo documentado; opciones 1–3 en H25). Cualquier retiro se decide al final.
4. Comprobación: el `.log` ya no debe traer `Label 'Cerqueira2020' multiply defined` ni `Citation 'XGBoost' undefined`; ninguna cita debe haber cambiado de número (comparar el texto de todas las `[n]` antes y después).

### Fase 3 — Capítulo 4: fusión de §4.1.3 y §4.1.8
Fuente: `H25_erratas.md` (c).

Fusionar con el texto verbatim propuesto, borrar la segunda `\subsection{Deep Learning}`, comprobar que la numeración queda §4.1.8 Entrenamiento mediante gradiente, §4.1.9 Perceptrón multicapa, §4.1.10 LSTM, y que el índice se actualiza (no hay `\ref` a esas secciones).

### Fase 4 — Capítulo 2 (contexto, fuentes, definiciones, figuras)
Fuentes: `R14_*`, `R15_*`, `R16_*`, `H26_*`, `figuras_cap2/`.

| Orden | Contenido | Notas |
|---|---|---|
| 4.1 | R14: fuentes y procesamiento (nueva §2.1) | Pendiente real: script original de construcción no localizado; el texto lo declara. Referencias del bloque nuevo [24]–[35] según cada borrador |
| 4.2 | R15: nueva §2.2 "Generación, consumo y demanda" | Ya incluye el párrafo de la serie anual del SIE y la terminología aprobada |
| 4.3 | R16: §2.3–§2.6 | Reemplaza "el SIN se divide en nueve regiones" (H17) y narra las Figs. 2.1–2.5 |
| 4.4 | Figuras 2.1, 2.2 y 2.5: sustituir los tres PNG y los `\caption` (líneas del `.tex` del 15/10: 574–575, 583–584, 608–609) | Nombres nuevos en `H26_revision_uso_de_consumo.md` §5. Las Figs. 2.3 y 2.4 también están regeneradas (títulos corregidos, H22) |
| 4.5 | Referencias nuevas **[24]–[35]** añadidas al final de `thebibliography`, con los datos de `R16_contexto_sistema_electrico.md` (Parte D) y `R14_fuentes_datos.tex`; las entradas con campos sin verificar (sección 3) se dejan incompletas, no se rellenan | Ocupan las posiciones 24 en adelante; no tocan las existentes. Campos aún sin verificar: ver sección 3 |

Terminología (decisión 22/10): "demanda eléctrica" para la variable pronosticada; "ventas de electricidad de CFE Suministro Básico" para las figuras del SIE, con la aclaración de que no es el consumo final del SEN. El **título de la tesis no cambia**.

Verificación: compilar; cada cifra del texto nuevo se contrasta con `datos_cap2/` y `figuras_cap2/datos_fig2_*.csv`; las figuras se revisan una por una a la vista (pie, ejes, unidades).

### Fase 5 — Capítulo 3: subsección STL
Fuente: `C3_subseccion_STL.md` (Parte A). Nueva §3.1.6 después de SARIMA; ecuación con `\label{eq:stl}` (numeración automática). Citas: [9] Cleveland, [16] Bergmeir, [17] Meng y Xu (existentes). La Parte B va en la fase 6.

### Fase 6 — Capítulo 5: metodología (R13) y Tabla 5.1
Fuentes: `R13_metodologia_general.md`, `C3_subseccion_STL.md` (Parte B), `H25_erratas.md` (d).

- Reescribir la descripción general con los siete pasos de R13 y las cuatro ventanas S1–S4.
- Tabla 5.1: la fila de ventana pasa a "cuatro semanas, S1–S4" (la tabla actual **está bien alineada**, no requiere arreglo de formato).
- Incluir la descripción de las estrategias con STL (Parte B de C3) y remitir a ella desde R13 para no duplicar.
- **[decisión]** Si se conserva "modernos" y la distinción moderna/histórica de los experimentos.
- **Condición previa:** cifras y tablas de S1–S4 completas (ver fase 7). Hasta entonces R13 se integra con la descripción del diseño, no con resultados.

### Fase 7 — Capítulos 6–7: resultados y conclusiones (depende del cómputo)
**Bloqueada** hasta terminar las 216 corridas y decidir H24/H27. Estado al 22/10:

| Componente | Estado |
|---|---|
| Colab, sesión A | Ensemble STL de S4 y S1 completado 8/8 (confirmado por el autor); faltan las demás configuraciones de A aún no completas |
| Colab, sesión B | Sin iniciar (S2 y S3, 56 configuraciones) |
| PC, SARIMAX T3/S3 | En curso (Gen 6/8 regiones; Imp, Exp y Temp-IGAE sin empezar) |
| H24 (XGBoost sin tuning efectivo) | Pendiente de decisión: declarar como limitación o corregir y repetir |
| H27 (LSTM directa con >10 intentos) | El autor ejecutará la auditoría en Colab; hasta tener el CSV no se modifican resultados, bases Optuna ni hiperparámetros |

Cuando se desbloquee: consolidar S1–S4 (`vt.consolidar_ventanas`), regenerar tablas/figuras, y redactar R20–R22 (explicación de Naive+T+S, resumen ARIMA/SARIMA, LSTM) con los datos de las cuatro semanas. Mapear conclusiones a los cinco objetivos (R10).

### Fase 8 — Estructura global (al final)
Fuente: `R12_estructura_tesis.md`. Nueva §0.4 "Estructura del documento", **solo después** de las fases 4–7, porque describe el contenido ya corregido. **[decisión]** R7 (¿qué estructura espera Roberto?) y R19 (renombrar "Metodología"): preguntar antes. El Cap. 3 de §0.4 debe mencionar STL (fase 5).

## 2. Verificación transversal después de cada fase

1. Compilar sin errores; comparar el `.log` con la línea base (no deben aparecer advertencias nuevas).
2. Todas las citas `[n]` resuelven; ninguna cambió de número salvo la de XGBoost ([?] → [12]).
3. Ecuaciones, figuras y tablas numeradas de forma continua; sin `\ref` rotas.
4. Cada cifra nueva del texto se rastrea a su CSV o a su fuente publicada (el borrador lo indica).
5. Búsqueda global de "consumo" en el `.tex` resultante: solo los usos permitidos (consumo final y bruto de SENER, título de la tabla del SIE, ejemplos generales, "consumo de memoria"). Ver `H26_revision_uso_de_consumo.md` §2.
6. Respaldo y commit del estado después de cada fase; el PDF de cada fase se conserva para comparar.

## 3. Pendientes de datos que bloquean partes del texto (no inventar)

| Pendiente | Afecta a | Qué falta |
|---|---|---|
| Páginas 785–794 de XGBoost en ACM | Fase 2 | Confirmar en `dl.acm.org/doi/10.1145/2939672.2939785` (respondió 403) |
| [24] INEGI, [25], [29] | Fase 4 | Título exacto, URL y fecha de consulta |
| [30] Plan 2025–2039 | Fase 4 | Fecha de publicación en el DOF |
| [33], [35] | Fase 4 | Títulos de portada exactos de los informes de SENER |
| [34] CFE, reporte 4T 2023 | Fase 4 | Fecha de publicación |
| Script original de construcción de las series | R14 | No localizado; el texto lo declara |
| Nombre oficial de las regiones | Fase 1 | Verificar en CENACE |
| Procedencia de `tab:lstm_resultados` | R22 | Script legacy perdido (bloquea R22) |

## 4. Decisiones del autor que siguen abiertas

Resueltas el 22/10 (segunda ronda): se mantiene el `.tex` del 15/10 como referencia provisional sin modificarlo; [19] Garcia se conserva y se revisa en la integración bibliográfica final; las páginas 785–794 de XGBoost se mantienen como "respaldadas por fuentes secundarias, pendientes de confirmación directa en ACM"; la fase de resultados sigue bloqueada hasta completar los experimentos y resolver H24/H27; R7, R19, R23 y R9 se consultan con Roberto. H24: el autor quiere corregirlo; antes se valida con el protocolo `docs/H24_PROTOCOLO_VALIDACION_TUNING_XGBOOST.md`.

Siguen abiertas:

1. Confirmar la versión vigente del `.tex` (puerta de entrada, sección 0).
2. [19] Garcia: conservar (opción 1), sustituir por una referencia nueva (opción 3) o retirar al final (opción 2).
3. Mantener o no "modernos" en §5.1.1.
4. R7 (estructura que espera Roberto), R19 ("Metodología" → "Experimentación"), R23 (¿XGBoost o ensamble nuevo?), R9 (dónde va Looker Studio).
5. H24: limitación o corrección de XGBoost.
6. H27: tras la auditoría, documentar, marcar o recalcular el ajuste final.
7. Título de la tesis: se conserva el actual provisionalmente.
