# Capítulo 3 — Subsección sobre la descomposición STL

| Campo | Contenido |
|---|---|
| **Qué resuelve** | El índice del Cap. 3 (PDF vigente) solo trae fundamentos, estacionariedad, ARIMA y SARIMA; la descomposición STL se cita en el Cap. 1 y en la Introducción ([9]) y se usa en el Cap. 5, pero no se explica. Afecta al objetivo específico 3 (R12, Parte B, hallazgo 1). |
| **Estado** | Redacción preparada (2026-10-22). **No integrada** en `tesis.tex`. |
| **Ubicación propuesta** | Nueva **§3.1.6 "Descomposición STL"**, después de §3.1.5 (SARIMA). La parte experimental (Parte B) va en el Cap. 5, dentro de la descripción de modelos. |
| **Fuentes** | Fundamento: Cleveland et al. [9] (ya en la bibliografía) y la documentación de statsmodels (que cita a [9]). Implementación: código real del repositorio (`models/{naive_trend_seasonal,ar_resid_trend_seasonal,fcnn,lstm_resid,ensemble_stl}`), `docs/MODELOS_MIGRADOS.md` y `docs/EXTENSION_CUATRO_SEMANAS.md`. |
| **Criterio** | La Parte A es teoría y no afirma nada sobre nuestros modelos; la Parte B describe solo lo que el código hace (ver la tabla de verificación de la Parte C). |

## Parte A — Texto propuesto para el Capítulo 3 (fundamento teórico)

### 3.1.6. Descomposición STL

La descomposición clásica de la sección 3.1.2 supone que la componente estacional $\eta_t$ se repite exactamente cada $d$ observaciones ($\eta_{t+d}=\eta_t$) y que la tendencia $\tau_t$ es una función suave. En series reales, como la demanda eléctrica horaria, el patrón estacional puede variar lentamente con el tiempo y los valores atípicos distorsionan el ajuste. El procedimiento STL (*Seasonal-Trend decomposition using LOESS*) [9] descompone una serie en tres componentes aditivos,

$$X_t = \tau_t + \eta_t + Y_t, \qquad t = 1,\dots,n, \tag{3.7}$$

donde $\tau_t$ es la tendencia, $\eta_t$ la componente estacional de periodo $d$ y $Y_t$ el residuo, pero **permite que $\eta_t$ cambie suavemente** de un ciclo a otro, en lugar de imponer que se repita. Las tres componentes se estiman con LOESS (*locally estimated scatterplot smoothing*), una regresión local ponderada que ajusta, alrededor de cada punto, un polinomio de bajo grado a sus vecinos más cercanos, dando más peso a los más próximos.

**Algoritmo.** STL alterna dos ciclos de cálculo [9]. En el **ciclo interno** se repite: (i) se resta a la serie la tendencia vigente; (ii) se suavizan con LOESS las *subseries de ciclo* (por ejemplo, todas las observaciones que ocupan la misma posición dentro del periodo); (iii) a esas subseries suavizadas se les aplica un filtro paso bajo para que la componente estacional no absorba variaciones lentas; (iv) la componente estacional es la diferencia entre ambas; (v) se resta la estacionalidad a la serie y la tendencia se vuelve a estimar con LOESS. En el **ciclo externo** se calculan *pesos de robustez* a partir del tamaño de los residuos, de modo que las observaciones con residuos muy grandes (valores atípicos) pesan menos en la siguiente pasada. Con la opción robusta, un valor atípico aislado apenas modifica la tendencia y la estacionalidad estimadas; esto es útil porque los eventos atípicos de una serie eléctrica no deben eliminarse (sección 4.2), pero tampoco deben gobernar el ajuste.

**Parámetros.** El resultado depende de (a) el periodo $d$ de la estacionalidad; (b) la longitud de la ventana de suavizado de la componente estacional (mayor longitud, estacionalidad más estable entre ciclos); (c) la longitud de la ventana de la tendencia (mayor longitud, tendencia más suave); y (d) el número de iteraciones de cada ciclo. Las implementaciones comunes fijan valores por defecto razonables para (b) y (c) a partir de $d$.

**Interpretación de los componentes.** La *tendencia* recoge el nivel de largo plazo de la serie; la *componente estacional*, el patrón que se repite con periodo $d$ (en datos horarios, el ciclo diario y semanal); y el *residuo*, lo que queda cuando se retiran ambos, es decir, las variaciones irregulares. La suma de las tres reconstruye exactamente la serie observada.

**Uso en pronóstico.** STL es una técnica de descomposición, no un modelo de pronóstico: no extrapola nada por sí misma. Para pronosticar, cada componente se proyecta hacia el futuro con un método distinto y se suman las proyecciones. Esta idea —separar estructuras de distinta naturaleza y tratarlas por separado— ya se ha usado con descomposición STL combinada con suavizamiento exponencial [16] y con redes neuronales para la carga eléctrica [17]. Dos observaciones prácticas: la descomposición debe calcularse **solo con los datos de entrenamiento** (si incluyera el periodo de prueba, la estimación de las componentes usaría información futura), y como LOESS es una regresión local, la estimación de la tendencia es menos precisa en los extremos de la ventana, justo donde se necesita para extrapolar.

## Parte B — Texto propuesto para el Capítulo 5 (procedimiento experimental)

### Estrategias basadas en STL

En todas las estrategias con descomposición, la serie de demanda de entrenamiento de cada región (3 600 horas) se descompone con la implementación `STL` de la biblioteca *statsmodels*, con periodo $d=168$ horas (una semana) y la opción robusta activada; los demás parámetros son los valores por defecto de la biblioteca. Con $d=168$ la componente estacional captura el patrón semanal, que incluye el diario; no se modela la estacionalidad anual, porque la ventana de entrenamiento abarca unos 150 días. La descomposición se calcula **únicamente con las 3 600 horas de entrenamiento**; las 168 horas de prueba no participan.

Las componentes se proyectan a las 168 horas de prueba así:

- **Tendencia:** se ajusta una recta (regresión lineal sobre el índice temporal) a la componente de tendencia del entrenamiento y se extrapola.
- **Estacionalidad:** se repiten las últimas 168 horas de la componente estacional del entrenamiento (con un horizonte de 168 horas, una sola copia).
- **Residuo:** se modela de forma distinta según la estrategia.

| Estrategia | Tendencia | Estacionalidad | Residuo |
|---|---|---|---|
| Naive + tendencia + estacionalidad | recta extrapolada | patrón repetido | se supone cero |
| AR sobre residuo STL | recta extrapolada | patrón repetido | modelo autorregresivo, con orden por AIC entre 1 y 168 rezagos |
| FCNN sobre residuo STL | recta extrapolada | patrón repetido | red completamente conectada, con variables exógenas, pronóstico recursivo; hiperparámetros con Optuna |
| LSTM sobre residuo STL | recta extrapolada | patrón repetido | red LSTM, con variables exógenas, pronóstico recursivo; hiperparámetros con Optuna |
| Ensemble STL | **LSTM** (con exógenas) | **FCNN** (con exógenas) | modelo autorregresivo, con orden por AIC entre 1 y 168 rezagos |

En el Ensemble STL el pronóstico final es la suma de los tres pronósticos de componentes; en las demás estrategias, la suma de la recta, el patrón repetido y el pronóstico (o el cero) del residuo. Estas estrategias se contrastan con el modelado directo de la demanda (objetivo específico 3).

## Parte C — Verificación contra el código (qué se comprobó y dónde)

| Afirmación del texto | Evidencia |
|---|---|
| STL de *statsmodels* con `period=168` y `robust=True` | `descomponer_stl` en `naive_trend_seasonal_model.py`, `ar_resid_trend_seasonal_model.py`, `fcnn_model.py`, `lstm_resid_model.py`, `ensemble_stl.py` (idéntica en los cinco) |
| Resto de parámetros por defecto de la biblioteca | No se pasa ningún otro argumento. Valores por defecto documentados en statsmodels 0.14.5: ventana estacional 7; tendencia y filtro paso bajo calculados a partir del periodo (para $d=168$: 321 y 169, por la regla documentada); grados de LOESS 1; con `robust=True`, 2 iteraciones internas y 15 externas (`STL.fit`). Los 321 y 169 son el resultado de aplicar la regla documentada, **no se leyeron de un atributo del objeto** |
| Solo el entrenamiento | `train = serie_reciente[:-forecast_horizon]` y `descomponer_stl(train)` en cada modelo; ventanas S1–S4 materializadas sin datos posteriores (`docs/EXTENSION_CUATRO_SEMANAS.md`, prueba `tests/test_windows.py`) |
| Tendencia: recta | `forecast_tendencia_lineal` (`LinearRegression` sobre el índice) |
| Estacionalidad: repetir el último periodo | `forecast_estacionalidad_repetida` (`np.tile` de las últimas 168 horas) |
| Naive + T + S: residuo cero | `pred_final = tendencia + estacionalidad` (`docs/MODELOS_MIGRADOS.md`) |
| AR sobre residuo: AIC entre 1 y 168 | `seleccionar_ar_por_aic`, `MAX_LAG_AR = 168`, `AutoReg(trend="c")` |
| FCNN y LSTM sobre residuo, con exógenas y recursivos | `fcnn_model.py` (estrategia 2) y `lstm_resid_model.py`; Optuna con 5 intentos (plan de corridas) |
| Ensemble STL: LSTM, FCNN y AR | `ensemble_stl.py` (docstring y `evaluar_region`); suma `trend_pred + seasonal_pred + resid_pred` |

## Parte D — Observaciones y pendientes

1. **El texto actual del Cap. 3 tiene dos erratas cercanas** (a revisar con H25): la frase "El modelo clásico de descomposición considere tendencia y **estacionariedad**" debería decir "considera tendencia y **estacionalidad**", y la ecuación de la descomposición clásica aparece numerada **(1.3)** dentro del Capítulo 3 porque lleva `\tag{1.3}` escrito a mano en `tesis.tex` (versión del 15/10, línea 657); ver `H25_erratas.md`, punto e. La ecuación nueva propuesta aquí figura como (3.7) solo de forma provisional: en LaTeX conviene ponerle `\label{eq:stl}` y dejar que se numere sola (la numeración final depende de cuántas ecuaciones haya antes en el capítulo y de si se quita la `\tag`).
2. **Referencias:** [9] (Cleveland et al., 1990), [16] (Bergmeir et al., 2016) y [17] (Meng y Xu, 2019) ya están en la bibliografía. Si se quiere citar la implementación, una entrada posible es la de la biblioteca *statsmodels* (Seabold y Perktold, 2010, *Proceedings of the 9th Python in Science Conference*); la incluyo solo como **candidata** y debe verificarse completa (páginas, enlace) antes de añadirla, porque no la comprobé contra la fuente en esta sesión.
3. **Lo que la teoría afirma y no se probó en esta tesis:** la menor precisión de LOESS en los extremos de la ventana es una propiedad general del método; no se midió su efecto en estas series. La explicación de los pesos de robustez y del filtro paso bajo sigue la descripción general de [9].
4. **Dependencia con R13/R12:** la Parte B repite, con otro nivel de detalle, parte de R13 (paso 5). Al integrar, conviene que R13 remita a esta subsección para no duplicar.
5. **Limitaciones del procedimiento experimental que pueden mencionarse en la discusión:** el periodo único de 168 horas, la recta como proyección de la tendencia y la repetición de un solo ciclo estacional son decisiones de diseño que simplifican la proyección de las componentes; no se evaluaron alternativas.
