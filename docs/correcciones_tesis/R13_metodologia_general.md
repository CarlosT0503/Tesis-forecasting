# R13 — Metodología general del trabajo

| Campo | Contenido |
|---|---|
| **Observación que resuelve** | R13 (Roberto): describir la metodología general, es decir, los pasos del trabajo de principio a fin. |
| **Estado** | Redacción preparada (2026-10-20). **No integrada** en `tesis.tex`. |
| **Ubicación propuesta** | Cap. 5, nueva §5.1 "Metodología general" (antes de la descripción modelo por modelo, que pasa a §5.2). Las tablas y resultados de modelos individuales del Cap. 5 actual quedan como referencia metodológica. |
| **Fuentes usadas** | Código: `src/tesis_forecast/{windows,config,runner,metrics}.py`, `data/exogenas.py`, `models/*.py`; plan: `docs/plan_corridas_ventanas.csv`; documentos: `docs/EXTENSION_CUATRO_SEMANAS.md`, `R14_cierre_procedencia_y_procesamiento.md`, `R14_fuentes_datos.md`, `R15_generacion_consumo_demanda.md`; PDF vigente (11) para contrastar con lo que hoy dice la tesis. |
| **Diseño descrito** | El **diseño definitivo**: cuatro semanas de prueba (S1–S4, la S4 es la semana original de la tesis). Lo que pertenece a experimentos anteriores se identifica en la Parte B y no se describe como diseño vigente. |
| **Depende de** | Los resultados de S1–S4 (en curso) solo para los capítulos 6 y 7; esta sección **no** depende de ellos. |

## Parte A — Texto propuesto (listo para integrar)

### 5.1. Metodología general

El trabajo sigue siete pasos: (1) obtención de los datos, (2) preparación de las series, (3) definición de las variables exógenas, (4) definición de las ventanas de entrenamiento y de prueba, (5) ajuste de los modelos, (6) generación de pronósticos y (7) evaluación con métricas de error. Todos los modelos se ajustan **por región, de forma independiente**, y todos pronostican **168 horas (una semana)**. La comparación entre estrategias solo se hace entre corridas que comparten región, semana de prueba y horizonte.

**Paso 1. Obtención de los datos.** La variable pronosticada es la demanda eléctrica horaria por balance, tomada de los reportes diarios *Estimación de la Demanda Real* de CENACE [31]. Se usan ocho series: las siete regiones del Sistema Interconectado Nacional (Central, Noreste, Noroeste, Norte, Occidental, Oriental y Peninsular) y el sistema de Baja California. Baja California Sur, que es un sistema aislado distinto y cuyos registros existen en los reportes, no forma parte del conjunto seleccionado: su incorporación queda como posible extensión del trabajo. Cada serie abarca del 1 de enero de 2019 al 23 de mayo de 2026 (64 800 registros horarios; 64 799 en Baja California), sin valores faltantes en la demanda. Junto con la demanda se extraen, de los mismos reportes, la generación, la importación y la exportación de cada región. Las variables económicas y climáticas son nacionales y mensuales: el Índice Global de Actividad Económica (IGAE) y sus componentes primario, secundario y terciario provienen de INEGI [24], y la temperatura promedio de la fuente descrita en [25]. (Ver R14 para la procedencia detallada y sus límites.)

**Paso 2. Preparación de las series.** (a) *Calendario.* Las series siguen la hora local, por lo que existen días de 23 horas (cambio de primavera) y de 25 horas (cambio de otoño, con la columna `Hora` llegando a 25); ningún cambio de horario cae dentro de las semanas de prueba. (b) *Valores atípicos.* No se eliminan, porque contienen información de eventos reales. (c) *Variables mensuales.* Las cinco series nacionales (temperatura, IGAE, primarias, secundarias y terciarias) son mensuales y se expanden a frecuencia horaria repitiendo el valor del mes. Como límite común de información se fijó marzo de 2026; después de esa fecha el último valor se mantiene constante (relleno hacia adelante), de modo que ninguna configuración tiene ventaja informativa sobre otra. (d) *Normalización.* En las redes neuronales las variables se estandarizan con media y desviación calculadas únicamente con los datos de entrenamiento. (e) *Descomposición STL.* En las estrategias con STL, la descomposición (periodo de 168 horas, versión robusta) se calcula solo sobre el entrenamiento.

**Paso 3. Variables exógenas y su tratamiento temporal.** Se consideran cinco variables: temperatura, IGAE, generación, importación y exportación. Cada una se evalúa de forma individual, en la combinación temperatura + IGAE y, en una configuración común, las cinco juntas; XGBoost y LightGBM incorporan además el IGAE desagregado en actividades primarias, secundarias y terciarias (ocho variables). La información que no se conocería al momento de pronosticar recibe un tratamiento que evita usar el futuro: la generación, la importación y la exportación entran con rezago de 168 horas (o con el promedio de los rezagos de 168 y 336 horas, según el modelo), de manera que siempre corresponden a instantes anteriores al inicio de la prueba. La temperatura y el IGAE entran con su valor del periodo; como terminan en marzo de 2026, en las semanas de prueba (26 de abril al 23 de mayo) toman un valor constante.

**Paso 4. Ventanas de entrenamiento y de prueba.** Se utilizan cuatro semanas de prueba consecutivas, de 168 horas cada una:

| Semana | Prueba (00:00 del primer día a 23:00 del último) |
|---|---|
| S1 | 26 de abril – 2 de mayo de 2026 |
| S2 | 3 – 9 de mayo de 2026 |
| S3 | 10 – 16 de mayo de 2026 |
| S4 | 17 – 23 de mayo de 2026 (semana de la comparación principal original) |

Para cada semana, el modelo recibe únicamente los datos hasta el último día de esa semana, y la prueba son las últimas 168 horas de esos datos; el entrenamiento son las horas inmediatamente anteriores. La longitud del entrenamiento depende de la familia de modelos: 3 600 horas para los modelos de referencia, AR, las estrategias con STL y las redes FCNN, LSTM sobre residuo y Ensemble STL; 2 160 horas para la LSTM directa; 1 440 horas para SARIMAX; y 336 horas para XGBoost y LightGBM. La optimización de hiperparámetros usa las últimas 168 horas del entrenamiento como validación, de modo que la semana de prueba nunca interviene. Con esta construcción no existe forma de que un modelo vea datos posteriores a la prueba; se verificó con una prueba automática en la que el futuro se alteró y las métricas de la semana no cambiaron.

**Paso 5. Modelos.** Se comparan cuatro grupos:

1. *Modelos de referencia:* Naive (repite el último valor observado del entrenamiento en todo el horizonte), Naive con tendencia (regresión lineal ajustada al entrenamiento y extrapolada) y Naive con tendencia y estacionalidad semanal (STL con periodo de 168 horas: tendencia lineal más el último patrón semanal repetido).
2. *Modelos estadísticos:* autorregresivo (AR) con orden elegido por AIC entre 1 y 168 rezagos; AR sobre el residuo de la descomposición STL (tendencia lineal y estacionalidad repetida más AR sobre el residuo); y SARIMAX(1,1,1)(1,0,1)₁₆₈ con las variables exógenas, cuyo orden se fija de antemano.
3. *Gradient boosting:* XGBoost y LightGBM, que reciben 168 rezagos de la demanda, medias y desviaciones móviles de 24 y 168 horas, un índice de tendencia y las variables exógenas; pronostican de forma recursiva. Los hiperparámetros se buscan con Optuna (10 intentos, semilla 42).
4. *Redes neuronales:* FCNN (1–2 capas densas con *dropout*) con ventana de 168 horas; LSTM directa que produce las 168 horas de una vez, con ventana de entrada de 24, 48 o 168 horas; y tres estrategias con STL: FCNN sobre el residuo (tendencia lineal y estacionalidad repetida), LSTM sobre el residuo, y el Ensemble STL, que pronostica la tendencia con una LSTM, la estacionalidad con una FCNN y el residuo con un AR, y suma los tres. Se entrenan hasta 60 épocas con detención temprana y se buscan hiperparámetros con Optuna (5 intentos en FCNN, LSTM sobre residuo y Ensemble STL; 10 en la LSTM directa).

**Paso 6. Pronóstico.** Los modelos de referencia, AR y SARIMAX producen las 168 horas directamente; XGBoost, LightGBM, la FCNN y la estrategia con residuo usan pronóstico recursivo (cada hora pronosticada se reutiliza como entrada); la LSTM directa produce el vector completo.

**Paso 7. Evaluación.** Se calculan MAE, RMSE, MAPE y sMAPE sobre las 168 horas de cada semana, por región (ecuaciones 5.1–5.4). El MAPE excluye las horas con demanda observada igual a cero y el sMAPE las de denominador cero. Los resultados se resumen por región, por semana y de forma global, con la media y la desviación estándar entre semanas, lo que permite medir no solo la magnitud del error sino su estabilidad.

**Reproducibilidad.** Cada corrida se identifica con un nombre determinista (modelo, horas de entrenamiento, horizonte, variables), usa la semilla 42 y guarda su configuración, la versión del código y los resultados parciales por región, de modo que una corrida interrumpida se reanuda sin repetir lo ya calculado.

## Parte B — Diseño definitivo frente a experimentos anteriores

| Aspecto | Diseño definitivo (describir) | Experimentos anteriores (no describir como vigentes) |
|---|---|---|
| Semanas de prueba | S1–S4, 168 h, todas con la misma construcción | Una sola semana (17–23 mayo 2026) como comparación principal |
| Regiones | Las 8 series con la misma longitud de entrenamiento por familia (336–3 600 h) | BCA con 384 h de entrenamiento (Tabla 6.5): no es una restricción de datos (H2) |
| Modelos de referencia (Naive, Naive+T, AR) | Ventana fija de 3 600 h / 168 h, comparables | División automática "max(720 h, 10 %)", no una semana (no comparable) |
| Alineación horaria | Etiquetas corregidas | Corridas con desfase de 1 h y sufijo `_timefix` (Naive+T+S, AR sobre residuo, FCNN, Ensemble STL, LSTM sobre residuo) |
| Univariados | Naive, Naive+T, Naive+T+S, AR, AR sobre residuo (ventana fija) | ARIMA(1,1,1), SARIMA univariado, STL+FCNN, LSTM individual (tablas 5.2–5.14, 6.4–6.5) |
| Horizontes | Solo 168 h | Pruebas con horizontes más largos |

## Parte C — Contrastes con el texto actual del Cap. 5 (corregir al integrar)

1. **"nueve de las ocho regiones"** (§5.1.1): errata; son ocho series (siete del SIN más Baja California).
2. **Baja California Sur**: el texto dice que no se incluyó "porque no se encontró una serie reciente". Reemplazar por la delimitación de alcance (Parte A, paso 1 y R16 §2.5). Ver H16.
3. **Una sola semana de prueba**: el Cap. 5 y la Tabla 5.1 describen solo el 17–23 de mayo. Con la extensión, presentar S1–S4 y tratar la S4 como la semana original.
4. **Tabla 5.1**: la fila "Ventana de entrada (DL)" y "Entrenamiento" aparecen desalineadas en el PDF; rehacer.
5. **Selección de órdenes de ARIMA/SARIMA**: la §5.1.8 atribuye el orden a ADF, KPSS, ACF y PACF; **no existe código ni resultado** de esas pruebas en el repositorio (H8). Los órdenes están fijados en el código. Aportar la evidencia o reformular ("órdenes fijados a priori").
6. **"Optuna cuando aplica"**: precisar qué modelos la usan (XGBoost, LightGBM, FCNN, LSTM directa, LSTM sobre residuo, Ensemble STL) y cuáles no (referencia, AR, AR sobre residuo, SARIMAX).

## Parte D — Limitaciones metodológicas que deben declararse

| # | Limitación | Evidencia | Hallazgo |
|---|---|---|---|
| 1 | Temperatura, IGAE y componentes terminan en marzo de 2026: en las cuatro semanas son constantes (relleno hacia adelante). | `data/exogenas.py` (`FECHA_CORTE_FIN`); EXTENSION §Decisión metodológica | H7 |
| 2 | Importación y exportación solo tienen valores reales en 2019; en 2020–2026 son constantes. | Archivos `*_IMP.csv`, `*_EXP.csv` | H3 |
| 3 | Las semanas de prueba son liquidación 0 (preliminar). Diferencia con la versión final ≈ 0.2 % de MAPE. | Verificación de R14 | H14 |
| 4 | El **ajuste de hiperparámetros de XGBoost no opera** en la configuración de 336 h: sus parámetros son los del primer intento de Optuna, idénticos en las ocho regiones (los 2 240 intentos de S1–S4 tienen valor infinito). LightGBM sí ajusta (ventana adaptativa). | Ver H24 | H24 |
| 5 | Los órdenes de ARIMA/SARIMA no se justifican con pruebas documentadas. | Ausencia de código | H8 |
| 6 | La procedencia del script original que construyó las series no se recuperó; el procedimiento se describe como reproducible, no como recuperado. | R14 | R14 |

## Parte E — Estado de los resultados que alimentan los capítulos 6 y 7

Al 2026-10-20 las 216 corridas del plan (54 por semana) están repartidas entre la PC (104: referencia, AR, SARIMAX, XGBoost, LightGBM) y Colab (112: las cuatro redes). La PC tenía 90 de 104 completas; el resto son corridas SARIMAX en curso. El estado de Colab no se pudo verificar desde el repositorio (ver el informe del 2026-10-20). Los cuadros de los capítulos 6 y 7 deben reescribirse con el consolidado (`vt.consolidar_ventanas`) cuando estén las 216.

## Referencias nuevas que usa esta sección
[24] INEGI, IGAE (pendiente de redactar), [25] fuente de la temperatura (pendiente, H6), [31] CENACE, *Estimación de la Demanda Real* (ver R15 Parte "Referencias").
