# R14 — Cierre: procedencia, cobertura, liquidaciones y procesamiento de las series regionales

| Campo | Contenido |
|---|---|
| **Observación que cierra** | R14 (procedencia, cobertura, frecuencia y limitaciones de los datos). **Sustituye** a `R14b_procedencia_series_regionales.md` (H14 y H15 ya resueltos) y complementa `R14_fuentes_datos.md` (fuentes exógenas). |
| **Estado** | Redacción preparada (2026-10-18). **No integrada** en `tesis.tex`. |
| **Ubicación propuesta** | Cap. 2, nueva §2.1 "Fuentes de información" → subsección "Datos regionales horarios" (párrafo y tabla de abajo); una frase en §5.1.1 con las ventanas efectivas. |
| **Referencia** | [31] CENACE — *Estimación de la Demanda Real*, Sistema de Información del Mercado: <https://www.cenace.gob.mx/Paginas/SIM/Reportes/EstimacionDemandaReal.aspx> (consultada 2026-10-18). |
| **Script de comprobación** | `scripts/verificar_procedencia_series.py` (solo lectura; **no** es el script original de construcción). |

## 1. Tres niveles que no deben confundirse

| Nivel | Qué es | Cobertura |
|---|---|---|
| **Datos originales** | 11 893 reportes diarios CSV de CENACE (*Estimación de la Demanda Real del Sistema – Por Balance*), en `Documentos Tesis/Archivozip.zip` | 2 700 días de operación consecutivos, 2019-01-01 a 2026-05-23, sin días ausentes; 1 a 5 versiones (liquidaciones 0–4) por día |
| **Serie procesada** | `{REGION}_long.csv`, una por región | 2019-01-01 00:00 a 2026-05-23 23:00 (tabla 2) |
| **Ventanas de los experimentos** | tramos de entrenamiento + 4 semanas de prueba | 2025-11-27 00:00 a 2026-05-23 23:00 (≈ 178 días, ~6.6 % de los 2 700 días) |

## 2. Tabla definitiva de las series procesadas

Hora = convención del reporte (`Hora` 1–24; la hora *h* cubre de *h*−1 a *h*; 25 el día de cambio de horario de otoño).

| Región | Filtro en el reporte (`Sistema` / `Area`) | Inicio | Fin | Registros | Días (23 h / 25 h) | Duplicados (fecha, hora) | Horas faltantes (excl. cambio de horario) | NaN demanda |
|---|---|---|---|---|---|---|---|---|
| BCA | BCA / BCA | 2019-01-01 00:00 | 2026-05-23 23:00 | 64 799 | 2 700 (8 / 7) | 0 | 0 | 0 |
| CEN | SIN / CEN | 2019-01-01 00:00 | 2026-05-23 23:00 | 64 800 | 2 700 (4 / 4) | 0 | 0 | 0 |
| NES | SIN / NES | idem | idem | 64 800 | 2 700 (4 / 4) | 0 | 0 | 0 |
| NOR | SIN / NOR | idem | idem | 64 800 | 2 700 (4 / 4) | 0 | 0 | 0 |
| NTE | SIN / NTE | idem | idem | 64 800 | 2 700 (4 / 4) | 0 | 0 | 0 |
| OCC | SIN / OCC | idem | idem | 64 800 | 2 700 (4 / 4) | 0 | 0 | 0 |
| ORI | SIN / ORI | idem | idem | 64 800 | 2 700 (4 / 4) | 0 | 0 | 0 |
| PEN | SIN / PEN | idem | idem | 64 800 | 2 700 (4 / 4) | 0 | 0 | 0 |

Cambio de horario: las regiones del SIN lo tuvieron hasta 2022 (4 días de 23 h y 4 de 25 h); BCA, que sigue el horario de verano de su zona, hasta 2026 (8 y 7; el último, 2026-03-08).

## 3. H15 resuelto — los "dos bloques BCA"

**Causa (demostrada en los reportes):** el reporte diario trae tres sistemas, `Sistema` = `BCA`, `BCS` y `SIN`. En los reportes de 2019 (comprobado el 2019-06-01) las filas de Baja California Sur llevan `Sistema = BCS` y `Area = BCS`; **desde el 2020-01-01 llevan `Sistema = BCS` pero `Area = BCA`**. Filtrar solo por `Area == "BCA"` devuelve entonces 48 filas por día (BCA y BCS mezcladas). Filtrando por **ambas columnas** (`Sistema == "BCA"` y `Area == "BCA"`) hay 24 filas por día.

**Qué bloque es la serie BCA de los experimentos:** el de `Sistema = BCA`, `Area = BCA`. Con ese filtro la serie procesada coincide con los reportes igual que las demás regiones (ver §4): 100 % de las 540 comparaciones de BCA (una de cada cinco fechas).

**Corrección a lo dicho en `R14b`:** el 11.6 % de coincidencia de BCA era un artefacto de filtrar solo por `Area`; BCA **no** tiene una transformación adicional.

**Consecuencia para BCS (hallazgo nuevo, H16):** la serie de Baja California Sur **sí existe** en los reportes desde 2020 (`Sistema = BCS`); el archivo `BCS_long.csv` disponible termina el 2020-06-15. La frase de la tesis "no se encontró una serie reciente de demanda para esa región" probablemente se debe a este etiquetado (verificable, no demostrado como causa).

## 4. H14 resuelto — versiones de liquidación

**Qué son** (CENACE): las estimaciones de demanda real "sirven de base para liquidar las transacciones" del Mercado Eléctrico Mayorista y CENACE "integra la información disponible que resulta en cada proceso de Liquidación" y de Re-Liquidaciones; la tabla de descarga indica el "No. de Liquidación Asociada" y la "Fecha de Publicación" (página oficial citada arriba). En los archivos: `LIQUIDACION k (Día de Operación: dd/mm/aaaa)`, con *k* de 0 a 4. La liquidación 0 es la primera versión publicada de un día de operación; las posteriores recalculan el día con información más completa. (El texto oficial no da plazos exactos; los de abajo se leen de las fechas de publicación de los archivos.)

**Regla aplicada en la serie procesada (comprobada por muestra):** para cada día se usa **la versión de mayor número que contiene datos**. Evidencia (muestra sistemática de 540 días, uno de cada cinco, × 8 regiones = 4 320 comparaciones, tolerancia 10⁻⁶ MWh):
- 4 232 coinciden con la versión de mayor número (98.0 %);
- las 88 restantes (11 días × 8 regiones, noviembre–diciembre de 2019 y 20-feb-2019) corresponden a días cuya liquidación 3 es un archivo **vacío** (solo encabezado, 9 líneas); la serie usa entonces la liquidación 2, es decir, la mayor con datos;
- total: **4 320 / 4 320** coinciden con la versión de mayor número con datos. La regla es consistente en las 8 regiones y en todos los años.

**Versión que corresponde a los datos de los experimentos** (según las versiones disponibles en el archivo): para los datos usados (desde 2025-11-27) y hasta 2026-02-14, liquidación 2; del 2026-02-15 al 2026-04-11, liquidación 1; **desde el 2026-04-12, solo liquidación 0**. Entonces: entrenamiento (desde 2025-11-27) = liquidaciones 2, 1 y 0, y **las cuatro semanas de prueba (26-abr a 23-may) = liquidación 0 (preliminar)**.

**Cuánto difiere la liquidación 0 de la versión final** (días donde existen ambas; muestra de 1 de cada 5 días, 8 regiones; error porcentual absoluto medio horario):

| Año | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|
| MAPE medio L0 vs versión final (%) | 0.16 | 0.34 | 0.20 | 0.14 | 0.20 | 0.15 | 0.13 | 0.17 |
| Percentil 95 (%) | 0.41 | 0.75 | 0.60 | 0.54 | 0.72 | 0.55 | 0.57 | 0.77 |
| Diferencia media (MWh por hora y región) | 6.3 | 16.2 | 11.0 | 8.3 | 12.8 | 8.8 | 7.5 | 9.0 |

**Implicación:** la incertidumbre del valor "real" de las semanas de prueba por ser preliminar es del orden de **0.2 % (p95 < 0.8 %)**, mucho menor que los errores de pronóstico de los modelos (MAPE de 2 % a 10 %), pero no nula. No se puede afirmar que las cifras de las cuatro semanas coincidan con las que CENACE publique tras re-liquidarlas. Limitación a declarar en Resultados.

**Los 72 archivos "no interpretados":** son días del 2022-01-13 al 2022-08-21 cuyos reportes de una de las liquidaciones usan otro formato de encabezado (`CLV_SISTEMA, CLV_AREA, HORA, GENERACION, IMPORTACION, EXPORTACION, ENERGIA ENTRE GERENCIAS, BALANCE`). **No afectan**: cada uno de esos 72 días tiene 5 versiones y, leyendo también ese formato, la serie procesada coincide con la versión de mayor número en **576 / 576** comparaciones (72 días × 8 regiones).

## 5. Procesamiento: comprobado frente a inferido

**Comprobado** (verificable en los archivos):
1. Fuente: reportes diarios de CENACE (*Por Balance*), 11 893 archivos, 2 700 días sin huecos.
2. Cada serie regional es el subconjunto de filas del reporte con `(Sistema, Area)` = (BCA, BCA) o (SIN, región).
3. Para cada día se usó la liquidación de mayor número con datos (§4).
4. No hay interpolación ni imputación: ninguna región tiene NaN en la demanda; los valores coinciden con el reporte a 10⁻⁶ MWh.
5. Se conserva la hora del reporte (`Hora` 1–24/25) y se agrega la columna `fecha` = día de operación.
6. El orden de columnas del CSV (`Sistema, Area, Hora, Generacion, Flujo Real de Importacion, Flujo Real de Exportacion, Estimacion…, fecha, Importacion Total, Exportacion Total, Intercambio neto…`) es el que resulta de concatenar los reportes diarios en orden cronológico agregando `fecha` a cada uno: coincide con esa construcción.
7. En 2019 los reportes traen `Flujo Real de Importacion/Exportacion`; desde 2020, `Importacion Total`, `Exportacion Total` e `Intercambio neto entre Gerencias` (ver R15 y H3).

**Inferido** (consistente con la evidencia, no demostrado):
- Que la unión fue una concatenación (p. ej. con `pandas.concat`) de los CSV diarios. El script original **no se localizó** (búsqueda en el repositorio, `Downloads`, `Documentos Tesis`).
- Que la selección de versión se hizo "la más reciente con datos al momento de la descarga".
- Que `{REGION}_GEN.csv`, `_IMP.csv` y `_EXP.csv` se derivaron de las columnas `Generacion`, `Flujo Real de Importacion` y `Flujo Real de Exportacion` de la misma tabla.

**Procedimiento reproducible** (descripción; **no** es el código original):
```text
para cada día d de 2019-01-01 a 2026-05-23:
    archivos(d) = reportes "Demanda Real Balance_<k> ... Dia Operacion d ..."
    versión(d)  = el archivo de mayor k cuyo cuerpo tiene filas
    tabla(d)    = filas del cuerpo (tras la línea "Sistema, Area, Hora, ...");  agregar fecha = d
serie = concatenar tabla(d) en orden cronológico
región r: filtrar (Sistema == "BCA" y Area == "BCA")   si r = BCA
          filtrar (Sistema == "SIN" y Area == r)       en otro caso
```
Una comprobación por muestra de este procedimiento está en `scripts/verificar_procedencia_series.py`.

## 6. Limitaciones y pendientes reales

- **Pendiente:** el script original de construcción no se encontró; las operaciones "inferidas" arriba no se pueden afirmar como código recuperado.
- **Verificación por muestra:** la regla de versión y la ecuación de balance se comprobaron en 1 de cada 5 días y en los 72 días de formato alterno (no en los 2 700); la conclusión es consistente, pero no exhaustiva.
- Las semanas de prueba son liquidación 0 (preliminar): declarar como limitación.
- BCS no se modeló aunque existe en los reportes desde 2020 (H16): decidir si se menciona o se amplía.
- Las columnas de flujo real de 2019 (importación/exportación) no se conservaron desde 2020 (H3).

## 7. Párrafo académico definitivo (sustituye al de `R14b`)

> Las series de demanda se construyeron a partir de los reportes diarios *Estimación de la Demanda Real del Sistema – Por Balance* que el CENACE publica en el Sistema de Información del Mercado [31]. Cada reporte corresponde a un día de operación y contiene, para cada región de control, un registro por hora (23 o 25 en los días de cambio de horario). Se reunieron 11 893 reportes que cubren sin interrupciones los 2 700 días comprendidos entre el 1 de enero de 2019 y el 23 de mayo de 2026. Para un mismo día pueden existir hasta cinco versiones, correspondientes a las liquidaciones 0 a 4 del mercado: la liquidación 0 es la primera estimación publicada y las posteriores recalculan el día con información más completa. Para cada día se empleó la versión de mayor número que contenía datos, de modo que las semanas de prueba, posteriores al 12 de abril de 2026, corresponden a la liquidación 0, de carácter preliminar; en una muestra de días, la diferencia media entre esa liquidación y la versión final es de aproximadamente 0.2 % (percentil 95 inferior a 0.8 %). Cada región se obtuvo filtrando el reporte por sistema y área (`Sistema = BCA` para Baja California y `Sistema = SIN` para las siete regiones restantes), lo que produce 64 800 observaciones horarias por región (64 799 en Baja California), sin valores faltantes ni registros duplicados. De esta cobertura, los experimentos emplearon únicamente el periodo del 27 de noviembre de 2025 al 23 de mayo de 2026, que incluye los tramos de entrenamiento de cada modelo y las cuatro semanas de prueba de 168 horas.
