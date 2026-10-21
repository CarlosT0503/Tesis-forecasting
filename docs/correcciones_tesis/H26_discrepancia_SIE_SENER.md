# H26 — Por qué el "consumo" del SIE y el consumo final de SENER difieren tanto

| Campo | Contenido |
|---|---|
| **Hallazgo** | La serie anual de la Fig. 2.2 (222.9 TWh en 2023) es ≈ 25 % menor que el consumo final del Sistema Eléctrico Nacional que reporta SENER (≈ 298.6 TWh en 2023). R15 y R16 las trataban como si midieran lo mismo. |
| **Estado** | **Explicado con evidencia documental** (identificación por coincidencia numérica; la ficha técnica del SIE no se encontró). Redacción propuesta lista; **requiere decisión del autor** sobre terminología y títulos de figuras. No integrado en `tesis.tex`. |
| **Fecha** | 2026-10-21. |

## 1. Conclusión

La tabla *Consumo de energía eléctrica por entidad federativa* del SIE reproduce, año por año y entidad por entidad, las **ventas de energía eléctrica de CFE Suministro Básico** (CFE SSB) que SENER publica en su *Informe Pormenorizado 2023*. Es decir, mide solo la energía vendida por el suministrador de servicios básicos: el suministro básico está previsto por ley para usuarios de menos de 1 MW, aunque la Tabla 30 del informe también incluye ventas a gran industria (27 989 GWh en 2023, que incorporan las de último recurso). **No incluye** el suministro calificado, ni los contratos de interconexión legados, ni los centros de carga abastecidos de forma remota, que sí forman parte del *consumo final* del SEN. Por eso la brecha existe y es esperable. El nombre "consumo" que usa el SIE es engañoso para esta serie.

**Cómo se llega a esta conclusión (y su límite):** no se localizó la ficha técnica del SIE que defina la tabla (su fuente declarada es el Anexo Estadístico del Informe de Gobierno). La identificación descansa en dos coincidencias numéricas independientes, descritas abajo, y en la nota de la propia tabla ("2010: incluye cifras de la extinta Luz y Fuerza del Centro"), coherente con ventas del servicio público. Es una identificación fuerte pero **inferida**, no una definición oficial.

## 2. Evidencia

### 2.1. Totales nacionales (GWh)

| Año | SIE (archivo local) | CFE SSB, Tabla 29 del Informe Pormenorizado 2023 |
|---|---|---|
| 2019 | 218 929.6 | 218 930 |
| 2020 | 206 564.1 | 206 564 |
| 2021 | 206 541.8 | 206 542 |
| 2022 | 214 593.7 | 214 594 |
| 2023 | 222 891.5 | 222 892 |

Coinciden al GWh en los cinco años. El informe añade que en 2023 las ventas de CFE SSB crecieron 3.9 % (222 892 frente a 214 594); el SIE da 3.87 %.

### 2.2. Variación por entidad federativa, 2023 / 2022

La Tabla 31 del informe (§4.1.2) da la variación porcentual del total de ventas de CFE SSB por entidad. Se comparó contra la variación calculada con el SIE: **las 32 entidades coinciden (diferencia 0.0 puntos porcentuales, a un decimal)**. Ejemplos: Campeche +10.2 %, Tabasco +12.4 %, Coahuila −5.7 %, Tlaxcala −5.1 %, Estado de México +3.3 %, Hidalgo −2.2 %. (Es poco verosímil que 32 variaciones de un decimal coincidan por azar entre dos series que midieran cosas distintas.)

### 2.3. Qué magnitudes de 2023 conviven (no son equivalentes)

| Magnitud | 2023 | Qué cubre | Fuente y estado |
|---|---|---|---|
| **Ventas de CFE Suministro Básico** (= tabla del SIE) | **222 892 GWh** | Energía vendida por CFE SSB a usuarios de servicio básico | Informe Pormenorizado 2023, §4.1.1, Tabla 29. **Verificada** |
| Suministro Calificado | 29 204 GWh | Usuarios con demanda ≥ 1 MW (CFE Suministro Calificado 9 051 + privados 20 152) | Informe Pormenorizado 2023, §4.2. **Verificada** |
| Comercialización total por modalidad | ≈ 288 000 GWh | Suma de suministro básico, calificado, contratos legados, comercializadores no suministradores y usuarios calificados participantes. El suministro básico fue 77.37 % | Informe Pormenorizado 2023, Gráfico 22 (cifra **derivada** de 222 892 / 0.7737; dato preliminar) |
| **Consumo final del SEN** | ≈ 298 600 GWh | Toda la energía comercializada por suministro básico, calificado (incluido último recurso y usuarios calificados participantes) y centros de carga abastecidos remotamente | Plan de Desarrollo del Sector Eléctrico 2025-2039, §2.1.1: 304 011 GWh en 2024, +1.8 % → 2023 **derivado** (el porcentaje está redondeado: 298.5–298.8 TWh) |
| Consumo neto del SEN | 345 439 GWh | Consumo final más pérdidas, usos propios del distribuidor y transportista y exportaciones netas | Informe Pormenorizado 2023, Gráfico 42 (CENACE). **Verificada** |
| Consumo bruto del SEN | ≈ 351 700 GWh | Incluye además autoabastecimiento remoto, pérdidas y usos propios de CFE | Plan 2025-2039, §2.1.4: 359 807 GWh en 2024, +2.3 % → 2023 **derivado**. Coincide con la generación total equivalente de PRODESEN 2023 (351 695 GWh) |

### 2.4. La brecha de 2023 (222.9 → ≈ 298.6 TWh)

- Se explican **29.2 TWh** con el suministro calificado (verificado).
- El resto (≈ 46 TWh frente al consumo final de SENER; ≈ 36 TWh frente a la suma por modalidad del Gráfico 22) corresponde a las demás modalidades: contratos de interconexión legados, comercializadores no suministradores, usuarios calificados que participan directamente en el mercado y centros de carga abastecidos de forma remota.
- **No pude cuantificar cada una** por separado y queda una diferencia de ≈ 10 TWh entre la suma por modalidad (≈ 288 TWh, preliminar) y el consumo final derivado (≈ 298.6 TWh). Puede deberse a la fecha de corte y reliquidación de los datos de CENACE o al redondeo de los porcentajes, pero **no está demostrado**.

### 2.5. Consecuencia para la *tendencia* de la serie (importante)

Desde la reforma de 2016 una parte de los usuarios migra del suministro básico al calificado. El Gráfico 22 muestra que la participación del suministro básico bajó de **88.77 % (2016) a 77.37 % (2023)**, y el informe dedica una sección a la migración de usuarios (§4.1.4). Por tanto la serie del SIE **subestima el crecimiento del consumo total** y su evolución mezcla dos efectos: la demanda real y el traspaso de usuarios a otra modalidad. Esto matiza las frases de R16 §2.4 sobre la evolución nacional (p. ej. "+27.1 % entre 2006 y 2023"): describen las ventas de CFE SSB, no el consumo del país.

## 3. Texto propuesto (listo para integrar en R15 §2.2 y R16 §2.4)

> **Sobre las cifras de consumo por entidad federativa.** La serie anual por entidad que publica el Sistema de Información Energética (SIE) bajo el nombre "consumo de energía eléctrica" coincide, en el total nacional de 2019 a 2023 y en la variación de 2023 de las 32 entidades, con las ventas de CFE Suministro Básico que reporta la Secretaría de Energía [33]. En consecuencia, en esta tesis se interpreta como la energía vendida por el suministrador de servicios básicos, y **no** como el consumo final del Sistema Eléctrico Nacional, que además incluye el suministro calificado, los contratos de interconexión legados y los centros de carga abastecidos de forma remota [30]. En 2023 las ventas de CFE Suministro Básico fueron 222 892 GWh [33], mientras que el consumo final del SEN fue de aproximadamente 298 600 GWh (calculado a partir de la cifra de 2024 y su variación [30]); la diferencia se debe a las modalidades de suministro no incluidas, de las cuales solo el suministro calificado (29 204 GWh en 2023 [33]) se pudo cuantificar con la información consultada. Como parte de los usuarios ha migrado del suministro básico al calificado desde 2016 [33], la serie del SIE subestima el crecimiento del consumo total. Las comparaciones de las Figuras 2.1, 2.2 y 2.5 deben leerse con esta cobertura.

## 4. Decisiones que requieren al autor

| # | Decisión | Opciones |
|---|---|---|
| 1 | **Terminología** de las Figs. 2.1, 2.2 y 2.5 y del texto del Cap. 2 | (a) conservar "consumo" y añadir la nota de cobertura; (b) renombrar a "ventas de energía eléctrica del suministro básico (CFE)". Recomendado: (b) en títulos y (a) en el texto corrido con la aclaración |
| 2 | Si se **acepta la identificación** por coincidencia numérica sin ficha técnica del SIE | Alternativa: pedir confirmación al SIE/SENER y citarla |
| 3 | Si se agrega la cifra del **consumo final** (≈ 298.6 TWh) como referencia, dado que es derivada | Alternativa: citar solo 2024 (304 011 GWh) que sí es cifra publicada |
| 4 | Alcance del contraste generación–consumo de la Fig. 2.5 | Observación: ambas series (generación bruta CFE+PIE y ventas de CFE SSB) tienen cobertura centrada en CFE, lo que hace más coherente la comparación; sigue sin ser un balance físico |

## 5. Referencias (nuevas; numeración propuesta, ver H23)

```latex
\bibitem{SENER_InformePormenorizado2023} Secretaría de Energía (2024). \emph{Informe pormenorizado sobre el desempeño y las tendencias de la industria eléctrica nacional 2023}, primera edición. https://www.gob.mx/cms/uploads/attachment/file/972693/Informe_Pormenorizado_2023.pdf (consultado el 21 de octubre de 2026).
\bibitem{CFE_Reporte4T2023} Comisión Federal de Electricidad (2024). \emph{Información financiera trimestral, consolidado, 4T 2023}. https://www.cfe.gob.mx/finanzas/reportes-financieros/Reportes\%20Trimestrales\%20Documentos/Reporte\%204Q\%202023.pdf (consultado el 21 de octubre de 2026).
```

| N.º | Documento | Dónde aparece lo citado | Verificación |
|---|---|---|---|
| [33] | SENER, *Informe Pormenorizado 2023* | §4.1.1 y Tablas 29–30 (ventas CFE SSB); §4.1.2 y Tabla 31 (por entidad); §4.2 (suministro calificado); Gráfico 22 (participación por modalidad); Gráfico 42 (consumo neto) | Leído en el PDF (107 pp.) |
| [34] | CFE, reporte 4T 2023 | Generación bruta 2023 = 253 265.116 GWh (incluye PIE), igual a la del SIE (253.2 TWh) | Leído en el PDF |
| [30] (existente) | SENER, Plan de Desarrollo del Sector Eléctrico 2025-2039 | §2.1.1 (consumo final 2024 = 304 011 GWh, +1.8 %) y §2.1.4 (consumo bruto 2024 = 359 807 GWh, +2.3 %) | Texto leído en una copia del capítulo 2; coincide con las definiciones ya verificadas en R15. La fecha de publicación en el DOF sigue pendiente |

## 6. Qué **no** está demostrado

1. La definición oficial de la tabla del SIE (solo hay identificación numérica).
2. El desglose de la brecha entre las modalidades distintas del suministro calificado.
3. La diferencia de ≈ 10 TWh entre el total por modalidad del Gráfico 22 y el consumo final derivado.
4. Que la correspondencia se mantenga antes de 2019 (solo se comparó 2019–2023 en totales y 2023/2022 por entidad); la nota de Luz y Fuerza del Centro (2010) es coherente pero no concluyente.
5. Las cifras derivadas (consumo final 2023, consumo bruto 2023, total por modalidad) dependen de porcentajes redondeados y de datos que el propio informe marca como preliminares.
6. Las participaciones del Gráfico 22 (88.77 % en 2016 y 77.37 % en 2023 para el suministro básico) se leyeron del texto extraído del gráfico en el PDF; conviene confirmarlas visualmente antes de citarlas.
