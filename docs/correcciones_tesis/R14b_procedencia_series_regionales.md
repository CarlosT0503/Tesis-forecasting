> **SUPERADO** por `R14_cierre_procedencia_y_procesamiento.md` (2026-10-18): H15 (BCA) y H14 (liquidaciones) resueltos; el 11.6 % de coincidencia de BCA era un artefacto de filtrar solo por `Area`.

# R14 (complemento) — Procedencia, longitud y cobertura de las series regionales de demanda

| Campo | Contenido |
|---|---|
| **Observación que cierra** | R14 (procedencia y cobertura de los datos). Complementa `R14_fuentes_datos.md` (sustituye su párrafo "Datos regionales horarios"). |
| **Estado** | Redacción preparada (2026-10-18). **No integrada** en `tesis.tex`. |
| **Ubicación propuesta** | Sección 2.1 "Fuentes de información", subsección "Datos regionales horarios", y una frase en §5.1.1 (ventanas efectivamente usadas). |
| **Referencias** | [20] CENACE (bibliografía existente). |

## Tres niveles que no deben confundirse

1. **Datos originales** (reportes diarios de CENACE): 11 893 archivos CSV, 2 700 días de operación consecutivos (2019-01-01 a 2026-05-23), sin ningún día ausente. Se conservan en `Documentos Tesis/Archivozip.zip`.
2. **Serie procesada** (`{REGION}_long.csv`): una serie horaria por región con los 2 700 días, de 2019-01-01 00:00 a 2026-05-23 23:00.
3. **Ventanas efectivas de los experimentos**: solo las últimas ~178 días de la serie procesada (ver abajo).

## Tabla compacta (serie procesada, ocho regiones)

La hora sigue la convención del reporte (`Hora` 1–24; la hora *h* cubre de *h*−1 a *h*). "Fin" es el inicio de la última hora (23:00 = hora 24).

| Región | Sistema / Área | Inicio | Fin | Registros | Días | Días de 23 h / 25 h | Registros duplicados (fecha, hora) | Horas faltantes fuera del cambio de horario | Valores NaN en demanda |
|---|---|---|---|---|---|---|---|---|---|
| BCA | BCA / BCA | 2019-01-01 00:00 | 2026-05-23 23:00 | 64 799 | 2 700 | 8 / 7 | 0 | 0 | 0 |
| CEN | SIN / CEN | 2019-01-01 00:00 | 2026-05-23 23:00 | 64 800 | 2 700 | 4 / 4 | 0 | 0 | 0 |
| NES | SIN / NES | 2019-01-01 00:00 | 2026-05-23 23:00 | 64 800 | 2 700 | 4 / 4 | 0 | 0 | 0 |
| NOR | SIN / NOR | 2019-01-01 00:00 | 2026-05-23 23:00 | 64 800 | 2 700 | 4 / 4 | 0 | 0 | 0 |
| NTE | SIN / NTE | 2019-01-01 00:00 | 2026-05-23 23:00 | 64 800 | 2 700 | 4 / 4 | 0 | 0 | 0 |
| OCC | SIN / OCC | 2019-01-01 00:00 | 2026-05-23 23:00 | 64 800 | 2 700 | 4 / 4 | 0 | 0 | 0 |
| ORI | SIN / ORI | 2019-01-01 00:00 | 2026-05-23 23:00 | 64 800 | 2 700 | 4 / 4 | 0 | 0 | 0 |
| PEN | SIN / PEN | 2019-01-01 00:00 | 2026-05-23 23:00 | 64 800 | 2 700 | 4 / 4 | 0 | 0 | 0 |

- **Horas faltantes = 0** respecto al calendario local: todo día tiene 24 registros, salvo los días de cambio de horario (23 h en primavera, 25 h en otoño, `Hora` hasta 25). Las regiones del SIN tuvieron cambio de horario hasta 2022 (4 + 4 días); BCA, que sigue el horario de verano, hasta 2026 (8 días de 23 h y 7 de 25 h; el último, 2026-03-08).
- **Duplicados = 0** pares (fecha, hora). (Bajo la convención hora−1 el registro `Hora = 25` coincide con la hora 1 del día siguiente; no es un duplicado en el archivo.)
- Fuente: `datos_locales/{REGION}_long.csv`, conteo del 2026-10-18. Archivo con `resultados_locales/cobertura_series_regionales.csv`.

### Ventanas efectivamente usadas por los experimentos

| Concepto | Valor |
|---|---|
| Semanas de prueba | S1 26-abr a 2-may, S2 3 a 9-may, S3 10 a 16-may, S4 17 a 23-may de 2026 (168 h cada una) |
| Entrenamiento más largo (3 600 h: FCNN, Ensemble STL, LSTM sobre residuos, STL-AR, Naive en la extensión) | desde el 2025-11-27 00:00 (S1) hasta el 2025-12-18 00:00 (S4); BCA una hora antes por su día de 23 h |
| Otros entrenamientos | SARIMAX 1 440 h, LSTM directa 2 160 h, XGBoost y LightGBM 336 h |
| **Cobertura total empleada** | **2025-11-27 00:00 a 2026-05-23 23:00 (≈ 178 días)** |
| Parte de la serie procesada que **no** se usó en estos experimentos | 2019-01-01 a 2025-11-26 (≈ 6.9 años) |

## ¿"Por Balance" o "Por Retiros"? — evidencia

**Por Balance** (demostrado en los archivos originales):
- Encabezado de cada reporte diario: *"Centro Nacional de Control de Energia — Estimacion de la Demanda Real del Sistema -Por Balance — Sistema Electrico Nacional — Reporte Diario"*, descargado del *Sistema de Información del Mercado (Área Pública)*.
- Los 11 893 nombres de archivo son de la forma `Demanda Real Balance_<k> Dia Operacion <fecha> v<fecha de publicación>.csv`; **ninguno** menciona "Retiros".
- La columna que se pronostica se llama `Estimacion de Demanda por Balance (MWh)`.

## Procesamiento que se pudo comprobar

El **script que construyó los `_long.csv` no está en el repositorio ni en los notebooks consultados** (búsqueda en `Downloads`, `Documentos Tesis` y el repositorio): **[PENDIENTE DE VERIFICAR]**. Lo siguiente se dedujo comparando los reportes con la serie procesada:

1. **Unión:** los reportes diarios se concatenaron, con una columna `fecha` igual al día de operación del encabezado; cada región es el subconjunto (`Sistema`, `Area`) del reporte (CEN, NES, NOR, NTE, OCC, ORI, PEN con `Sistema = SIN`; BCA con `Sistema = BCA`).
2. **Versión de liquidación:** para un mismo día existen de 1 a 5 versiones (liquidaciones 0 a 4, archivos `_0` … `_4`). En CEN, NES, NOR, NTE, OCC, ORI y PEN la serie procesada **coincide, día por día y hora por hora (tolerancia 10⁻⁶ MWh), con la versión de liquidación más alta disponible en 98.1 % de los días-región comparables** (y solo en 1.6–2.4 % con la más baja). Es decir, se usó la liquidación más reciente de cada día.
3. **Consecuencia para las semanas de prueba:** desde el 12 de abril de 2026 solo existe la liquidación 0 (preliminar), por lo que **las cuatro semanas de prueba corresponden a la liquidación 0**; los días anteriores a esa fecha, a liquidaciones posteriores.
4. **Columnas auxiliares:** en 2019 los reportes traen `Flujo Real de Importacion/Exportacion`; desde 2020, `Importacion Total`, `Exportacion Total` e `Intercambio neto entre Gerencias`. La serie unida conserva ambas familias de columnas (las del flujo real quedan vacías desde 2020; ver H3).
5. **Sin interpolación ni imputación** de la demanda: no hay NaN en ninguna región (las carpetas `Regiones imputadas SARIMA promedio` son otro trabajo).

**Pendientes de verificar (no se pudieron demostrar):**
- **BCA:** a partir de 2020 el reporte diario contiene dos bloques con `Area = BCA` (48 registros por día) y la serie procesada conserva 24; la comparación **no fue concluyente** (11.6 % de coincidencia) y no se determinó cuál bloque o regla de selección se aplicó.
- **72 archivos** (liquidación 3, p. ej. 2022-01-13 en adelante) tienen un formato que el lector de esta comprobación no interpretó; no afectan a las conclusiones anteriores, pero no se compararon.
- El script de construcción y el criterio exacto para elegir la versión (¿la más reciente al momento de descargar?).

## Párrafo académico (listo para la tesis)

> Las series de demanda se construyeron a partir de los reportes diarios *Estimación de la Demanda Real del Sistema – Por Balance* que el CENACE publica en el Sistema de Información del Mercado [20]. Cada reporte corresponde a un día de operación y contiene, para cada región de control, un registro por hora (23 o 25 en los días de cambio de horario). Se reunieron 11 893 reportes que cubren, sin interrupciones, los 2 700 días comprendidos entre el 1 de enero de 2019 y el 23 de mayo de 2026; para un mismo día pueden existir hasta cinco versiones, correspondientes a las liquidaciones 0 a 4 del mercado. En las regiones del Sistema Interconectado Nacional (CEN, NES, NOR, NTE, OCC, ORI y PEN) la serie procesada coincide con la liquidación más reciente disponible para cada día, por lo que las semanas de prueba, posteriores al 12 de abril de 2026, corresponden a la liquidación 0, de carácter preliminar. Cada serie regional consta de 64 800 observaciones horarias (64 799 en BCA, por su calendario de horario de verano), sin valores faltantes ni registros duplicados. De esta cobertura, los experimentos emplearon únicamente el periodo comprendido entre el 27 de noviembre de 2025 y el 23 de mayo de 2026, que incluye los tramos de entrenamiento de cada modelo y las cuatro semanas de prueba de 168 horas.

(En el texto final, quitar o confirmar la frase sobre BCA y la regla de selección si no se verifica; ver pendientes.)

## Evidencia reproducible
- Conteos: `resultados_locales/cobertura_series_regionales.csv` (generado de `datos_locales/*_long.csv`).
- Comparación contra reportes: script de análisis de esta sesión (lee `Archivozip.zip` sin modificarlo); resultado resumido arriba.
