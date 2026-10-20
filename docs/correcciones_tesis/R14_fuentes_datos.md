# R14 — Procedencia, cobertura, frecuencia y limitaciones de los datos

| Campo | Contenido |
|---|---|
| **Observación que resuelve** | R14 (Roberto, nota amarilla al inicio del Cap. 2): *"Primero explica de dónde sacaste los datos, qué fuentes había, limitantes."* |
| **Estado** | Redacción preparada (2026-10-17). **No integrada** en `tesis.tex` ni en el PDF vigente. |
| **Ubicación propuesta** | Capítulo 2 (*Generación Eléctrica en México*): nueva **Sección 2.1 "Fuentes de información"**, antes del párrafo actual "Este capítulo inicia con un análisis descriptivo…" (que pasaría a 2.2). Referencia cruzada desde §5.1.1 *Configuración experimental* (una frase: "Los datos se describen en la Sección 2.1."). |
| **Referencias** | [31] CENACE, *Estimación de la Demanda Real* (nueva; la [20] existente es otra página) · [21] SIE/SENER (ya en la bibliografía) · **[24] INEGI, IGAE (nueva, por completar)** · **[25] fuente de la serie de temperatura (por confirmar)**. |
| **Archivo LaTeX equivalente** | `R14_fuentes_datos.tex` (misma redacción, listo para pegar; usa `\cite{CENACE}` y `\cite{SIE}`, claves existentes). |
| **Relacionadas, NO adelantadas** | R15 (definir generación y consumo) y R16 (contexto de México) irán después en 2.2 y 2.3. |

Los datos de este texto salen de los archivos de trabajo (copias locales; MD5 en
`docs/datos_locales_MD5SUMS.txt`) y de las notas de esos archivos. Todo lo que no se
pudo respaldar queda entre corchetes **[VERIFICAR]** y listado al final.

---

## Texto propuesto

### 2.1. Fuentes de información

Los datos de esta tesis proceden de fuentes institucionales de acceso público. Se emplearon dos tipos de información: series anuales y mensuales por entidad federativa, que sustentan el análisis descriptivo de este capítulo, y series horarias por región del Sistema Eléctrico Nacional, que constituyen la base de los experimentos de pronóstico de los capítulos siguientes.

**Datos por entidad federativa.** El consumo y la generación de energía eléctrica por entidad federativa se obtuvieron del Sistema de Información Energética (SIE) de la Secretaría de Energía [21]. El consumo se publica con frecuencia anual, en gigawatts-hora, y el archivo utilizado abarca de 2006 a 2024; sus cifras de 2024 están actualizadas solo hasta junio, de modo que ese año está incompleto y no es comparable con los años completos. La generación corresponde a la generación bruta de la Comisión Federal de Electricidad (CFE) más los Productores Independientes de Energía (PIE), se publica con frecuencia mensual, en megawatts-hora, y el archivo descargado cubre de enero de 2002 a marzo de 2025; el análisis de este capítulo emplea los registros hasta diciembre de 2024 **[VERIFICAR]**. Por su denominación, esta serie se limita a la generación de CFE y de los PIE.

**Datos regionales horarios.** Las series que se pronostican y las variables de generación, importación y exportación proceden del Centro Nacional de Control de Energía (CENACE) [31], organismo que opera el Sistema Eléctrico Nacional. La información se organiza por región de control: Baja California (BCA), Central (CEN), Noreste (NES), Noroeste (NOR), Norte (NTE), Occidental (OCC), Oriental (ORI) y Peninsular (PEN). El estudio comprende las siete regiones del Sistema Interconectado Nacional (Central, Noreste, Noroeste, Norte, Occidental, Oriental y Peninsular) y el sistema de Baja California. Baja California Sur es un sistema separado, cuyos registros existen en los reportes de CENACE, pero no forma parte del conjunto de regiones seleccionadas; esta es una delimitación del alcance del trabajo, y su incorporación puede considerarse como una extensión futura. Para cada región y cada hora se dispone de la estimación de demanda por balance, la generación y los flujos reales de importación y de exportación, todos en megawatts-hora. La variable que se pronostica es la estimación de demanda por balance; se trata, por tanto, de una estimación y no de una medición directa del consumo.

**Variables exógenas económicas y climáticas.** La actividad económica se representó con el Indicador Global de la Actividad Económica (IGAE) del Instituto Nacional de Estadística y Geografía (INEGI) [24]: un índice mensual de volumen físico con base 2018 = 100, de cobertura nacional, disponible para el total y para las actividades primarias, secundarias y terciarias. La temperatura se tomó de una serie de temperatura promedio de frecuencia mensual [25] **[VERIFICAR fuente y unidad]**. El archivo del IGAE incluye, después de cada año, una columna con el total anual; esas columnas se eliminaron para conservar únicamente los valores mensuales.

### 2.1.1. Cobertura temporal y frecuencia

La Tabla 2.1 resume las series utilizadas. Las series regionales de CENACE abarcan del 1 de enero de 2019 al 23 de mayo de 2026, es decir, 2 700 días con registro horario en cada región (64 800 registros, 64 799 en BCA). Los registros siguen la hora local, por lo que los días del cambio de horario tienen 23 o 25 horas y el campo de hora llega a 25 en estos últimos; en las regiones distintas de BCA los cambios de horario ocurren hasta 2022, y en BCA hasta 2026. En el periodo analizado la demanda y la generación no presentan valores faltantes.

**Tabla 2.1.** Fuentes, frecuencia y cobertura de los datos.

| Variable | Fuente | Frecuencia original | Cobertura en el archivo | Uso |
|---|---|---|---|---|
| Consumo por entidad federativa | SIE-SENER [21] | Anual | 2006–2024 (2024 hasta junio) | Análisis descriptivo |
| Generación bruta por entidad federativa | SIE-SENER [21], con información de CFE | Mensual | Ene 2002 – mar 2025 | Análisis descriptivo |
| Demanda (estimación por balance) por región | CENACE [31] | Horaria | 2019-01-01 a 2026-05-23 | Variable pronosticada |
| Generación por región | CENACE [31] | Horaria | 2019-01-01 a 2026-05-23 | Variable exógena |
| Importación y exportación por región | CENACE [31] | Horaria | Ver limitación (iv) | Variable exógena |
| IGAE (total y por actividad) | INEGI [24] | Mensual | Ene 1993 – mar 2026 (se usa desde ene 2019) | Variable exógena |
| Temperatura promedio | [25] | Mensual | Ene 2002 – mar 2026 (se usa desde ene 2019) | Variable exógena |

Las series mensuales (IGAE y temperatura) se convirtieron a frecuencia horaria repitiendo el valor del mes en cada una de sus horas, sin interpolación; por ello, dentro de un mismo mes estas variables son constantes.

### 2.1.2. Disponibilidad de las variables exógenas y fecha de corte

Para que todas las configuraciones experimentales dispusieran de la misma información exógena, se fijó una **fecha de corte común**: las series globales (IGAE, sus componentes por actividad y temperatura) se utilizaron hasta marzo de 2026. Esa fecha no tiene un significado particular; es el límite de información exógena compartido por todos los experimentos y evita que una configuración tenga ventaja informativa sobre otra. A partir del corte se conserva el último valor disponible (relleno hacia adelante), de modo que en las semanas de prueba, todas posteriores a marzo de 2026, estas variables permanecen constantes y no aportan variación.

Las variables exógenas se clasificaron además según su disponibilidad al momento de pronosticar. La temperatura y el IGAE se trataron como conocidas durante el horizonte. La generación, la importación y la exportación no se conocen con anticipación, por lo que sus valores reales nunca se utilizaron en el horizonte de pronóstico, sino una aproximación construida con semanas previas: el promedio de la misma hora una y dos semanas antes (XGBoost, LightGBM y SARIMAX; en los dos primeros también las componentes primaria, secundaria y terciaria del IGAE), el valor de la misma hora una semana antes (LSTM directa y LSTM sobre residuos) o un desplazamiento de 168 horas de la serie completa (FCNN y Ensemble STL).

### 2.1.3. Limitaciones de los datos

(i) La variable pronosticada es una estimación de demanda por balance, no una medición directa. (ii) Baja California Sur queda fuera del alcance del estudio (delimitación, no falta de datos); puede considerarse como extensión futura. (iii) El consumo por entidad federativa es anual y su último año (2024) está incompleto, por lo que las comparaciones entre años deben excluirlo o interpretarlo con cautela; la generación por entidad corresponde solo a CFE y PIE. **(iv) [INCLUIR SOLO SI SE CONFIRMA EN LA COPIA DE DRIVE]** Los archivos de importación y exportación proceden de las columnas de flujo real de CENACE, que solo contienen valores en 2019; desde 2020 esas variables carecen de dato real y, tras el relleno de valores faltantes, se mantienen constantes. (v) El IGAE y la temperatura son mensuales y se expandieron a horas de forma plana; sus últimos meses disponibles pueden ser preliminares. (vi) La fecha de corte común implica que las variables globales no varían en las cuatro semanas de prueba. (vii) Las series regionales incluyen los cambios de horario descritos arriba.

---

## Verificación de cada afirmación

| Afirmación | Evidencia |
|---|---|
| Consumo SIE: anual, GWh, 2006–2024, cifras de 2024 a junio | `Consumo de energia electrica por entidad federativa.csv`: encabezado "Sistema de Información Energética – Secretaría de Energía", "(Gigawatts-hora)", columnas 2006…2024; nota "Cifras al mes de junio 2024"; total nacional 2024 = 106 862.6 frente a 222 891.5 en 2023. |
| Generación SIE: CFE + PIE, mensual, MWh, ene 2002 – mar 2025 | `Generación bruta de energía eléctrica por entidad federativa.csv`: título "Generación Bruta de CFE mas PIE´s por Entidad Federativa", "(megawatts-hora)", columnas ENE/2002…MAR/2025; nota "Fuente: Sistema de Información Energética (SIE) con información de CFE". El notebook `Generacion electrica por estado.ipynb` descarta las últimas 3 columnas (`iloc[:, :-3]`) → hasta DIC/2024. |
| Regiones CENACE: columnas y unidades | `{REGION}_long.csv`: `Sistema, Area, Hora, Generacion (MWh), Flujo Real de Importacion (MWh), Flujo Real de Exportacion (MWh), Estimacion de Demanda por Balance (MWh), fecha, Importacion Total (MWh), Exportacion Total (MWh), Intercambio neto entre Gerencias (MWh)`. La atribución a CENACE sigue la indicación del autor; el CSV no trae una línea de fuente. |
| 2019-01-01 – 2026-05-23, 2 700 días, 64 800 registros (BCA 64 799), sin NaN en demanda ni generación | Auditoría `ventanas_tools.auditar_datos_ventanas` y conteo por región (2026-10-17). |
| Días de 23/25 h | CEN, NES, NOR, NTE, OCC, ORI, PEN: 23 h el 2019-04-07, 2020-04-05, 2021-04-04, 2022-04-03; 25 h en 4 fechas (2019-10-27, 2020-10-25, 2021-10-31, 2022-10-30). BCA: 23 h en 8 fechas (2019-03-10 … 2026-03-08); 25 h en 7 (2019-11-03 … 2025-11-02). |
| IGAE: INEGI, base 2018, mensual, nacional, ene 1993 – mar 2026 | `IGAE_2.xlsx`, hoja `MetaInfo`: "INEGI", "FRECUENCIA: Mensual", "COBERTURA GEOGRÁFICA: Nacional", "EVENTO: Año base 2018", "COBERTURA TEMPORAL: 1993-01-2026-03"; hoja `Tabulado`: "Serie de enero de 1993 a marzo de 2026". Últimos meses marcados `R` (revisado) y `P` (preliminar). |
| Columnas "Anual" eliminadas | En `Tabulado` las posiciones 13, 26, 39, 52… de la fila de meses son "Anual"; `drop_every_13th` elimina cada 13.º valor. |
| Temperatura: mensual, ene 2002 – mar 2026 | `Temperaturas promedio.csv`: fila "Mes" ene-02 … mar-26 (291 meses); fila "Promedio". El archivo no indica fuente ni unidad. |
| Se usa desde ene 2019 y hasta mar 2026 | `data/exogenas.py`: `FECHA_CORTE_INICIO = 2019-01-01`, `FECHA_CORTE_FIN = 2026-03-01` (mes inclusive; último dato horario 2026-03-31). |
| Expansión plana mensual → horaria | `expandir_exogena` (`data/exogenas.py`). |
| Conocidas / no conocidas y mecanismos | Código: `xgboost_model.construir_future_exog`, `sarimax_model.construir_exogenas_futuras`, `lstm_direct.construir_future_exog_directa`, `fcnn_model.preparar_exogena_lag168`; `docs/MODELOS_MIGRADOS.md`. |
| Constantes desde abril de 2026 | `merge_exogenas` / `alinear_exogenas_*` aplican `ffill`; auditoría: último dato real 2026-03-31 en las cinco series; 26/33/40/47 días antes de S1/S2/S3/S4. |
| Importación/exportación solo con valor en 2019 | Archivos `*_IMP.csv`/`*_EXP.csv`: 8 759 valores no nulos de ~64 800 por región; último 2019-12-31. En `{REGION}_long.csv`, `Importacion Total`/`Exportacion Total` existen de 2020 en adelante pero no se extrajeron. |

## Pendientes de verificar antes de integrar

1. **Fuente y unidad de la temperatura** (el archivo no las indica) → completar [25] y la frase de §2.1.
2. **Referencia INEGI [24]**: completar con título, URL y fecha de consulta (el título del archivo es "Indicador Global de la Actividad Económica. Año Base 2018", serie ene 1993 – mar 2026).
3. **Nombre exacto del reporte de CENACE** del que se descargaron las series horarias por región. La referencia [20] es "Energía Generada por Tipo de Tecnología"; si los datos horarios salen de otro reporte, conviene una referencia específica.
4. **Confirmar que los archivos de Drive son idénticos a estas copias locales** (comparar MD5 con `docs/datos_locales_MD5SUMS.txt`). Si difieren, rehacer las cifras de §2.1.1.
5. **Importación y exportación (limitación iv):** confirmar en la copia de Drive y decidir si se redacta tal cual, si se documenta como limitación o si se corrigen las series (decisión metodológica del autor).
6. **Periodo del Capítulo 2.** La tesis dice "entre enero de 2001 y diciembre de 2024", pero los archivos dan consumo anual 2006–2024 y generación mensual desde enero de 2002. Hay que reconciliar esa frase con las Figuras 2.1–2.5 (R15/R16 la tocarán).
7. **Figura 2.2 y "reducción en 2024".** Si la figura usa el consumo anual del SIE, el 2024 corresponde solo a enero–junio (106 862.6 GWh frente a 222 891.5 en 2023): esa "reducción" sería un artefacto de datos incompletos, no una caída del consumo. Verificar con el notebook de la figura.
8. **Último mes del IGAE.** Los meses más recientes llevan marcas `R`/`P`; confirmar el estado de marzo de 2026 si se quiere citar como "preliminar".
9. **Mecanismos de aproximación (§2.1.2):** si se prefiere, trasladar ese párrafo a la Metodología y dejar en 2.1 solo la fecha de corte.
