# H26 — Por qué el "consumo" del SIE y el consumo final de SENER difieren tanto

| Campo | Contenido |
|---|---|
| **Hallazgo** | La serie anual de la Fig. 2.2 (222.9 TWh en 2023) es menor que el consumo final del Sistema Eléctrico Nacional que reporta SENER. R15 y R16 las trataban como si midieran lo mismo. |
| **Estado** | **Explicado como inferencia respaldada por coincidencias numéricas** (no es una confirmación oficial del SIE). Decisiones del autor del 2026-10-22 incorporadas. Revisión del uso de "consumo" en la tesis y en los borradores: `H26_revision_uso_de_consumo.md`. No integrado en `tesis.tex`. |
| **Actualización** | 2026-10-22: se reemplazaron las cifras derivadas de porcentajes redondeados por cifras publicadas del mismo año (2024) y se regeneraron las figuras 2.1, 2.2 y 2.5 con la denominación nueva. |

## 1. Conclusión (como inferencia)

La tabla *Consumo de energía eléctrica por entidad federativa* del SIE **coincide numéricamente**, año por año y entidad por entidad, con las **ventas de energía eléctrica de CFE Suministro Básico (CFE SSB)** que SENER publica en sus informes pormenorizados. Se infiere que mide la energía vendida por el suministrador de servicios básicos y **no** el consumo final del SEN, que además incluye el suministro calificado y otras modalidades. El SIE no publica (en lo que se pudo consultar) una definición de esta tabla; su fuente declarada es el Anexo Estadístico del Informe de Gobierno. La identificación se apoya en las evidencias de la sección 2 y en la nota de la tabla ("2010: incluye cifras de la extinta Luz y Fuerza del Centro"), coherente con ventas del servicio público. **Debe presentarse como inferencia**, no como definición oficial.

## 2. Evidencia

### 2.1. Totales nacionales (GWh)

| Año | SIE (archivo local) | CFE SSB (SENER) | Fuente SENER |
|---|---|---|---|
| 2019 | 218 929.6 | 218 930 | Informe Pormenorizado 2023, Tabla 29 |
| 2020 | 206 564.1 | 206 564 | ídem |
| 2021 | 206 541.8 | 206 542 | ídem |
| 2022 | 214 593.7 | 214 594 | ídem |
| 2023 | 222 891.5 | 222 892 | ídem; reconfirmado en el Informe Pormenorizado 2024 |
| 2024 | 106 862.6 (solo hasta junio) | **225 213** | Informe Pormenorizado 2024, §4.1.1 (crece 1.0 %) |

Coinciden al GWh en 2019–2023. El SIE de 2024 está incompleto (enero–junio), por lo que no es comparable con el dato anual de SENER.

### 2.2. Variación por entidad, 2023 / 2022

La Tabla 31 del Informe Pormenorizado 2023 (§4.1.2) da la variación porcentual del total de ventas de CFE SSB por entidad. Contra la variación calculada con el SIE: **las 32 entidades coinciden (diferencia 0.0 pp a un decimal)** (ejemplos: Campeche +10.2 %, Tabasco +12.4 %, Coahuila −5.7 %, Tlaxcala −5.1 %, Hidalgo −2.2 %). Es poco verosímil que 32 variaciones de un decimal coincidan por azar entre series que midieran cosas distintas. (Comprobación hecha con la extracción en modo "raw" del PDF; la extracción por maquetación daba filas desordenadas.)

## 3. Magnitudes publicadas de 2023 y 2024 (solo cifras publicadas)

| Magnitud | 2023 | 2024 | Qué cubre | Fuente |
|---|---|---|---|---|
| **Ventas de CFE Suministro Básico** (= tabla del SIE) | 222 892 | **225 213** | Energía vendida por CFE SSB | Inf. Pormenorizado 2023 (Tabla 29) y 2024 (§4.1.1) |
| Suministro calificado | 29 204 | **37 177** | Usuarios con demanda ≥ 1 MW (2024: CFE 9 672 + privados 27 505) | Inf. Pormenorizado 2023 §4.2 y 2024 §4.2 |
| **Consumo final del SEN** | no publicada en las fuentes consultadas | **304 011** | Energía comercializada por suministro básico, calificado (incluido último recurso y usuarios calificados participantes) y centros de carga abastecidos remotamente | Plan de Desarrollo del Sector Eléctrico 2025-2039, §2.1.1 |
| Consumo neto del SEN | 345 439 | 351 933 | Consumo final más pérdidas, usos propios y exportaciones netas | Inf. Pormenorizado 2023 (Gráfico 42) y 2024 (Gráfico 37) |
| Consumo bruto del SEN | no publicada en las fuentes consultadas | 359 807 | Incluye además autoabastecimiento remoto, pérdidas y usos propios de CFE | Plan 2025-2039, §2.1.4 |

No se usan cifras de 2023 derivadas de variaciones porcentuales redondeadas (por ejemplo, consumo final 2023 a partir de "+1.8 %"). Quedan solo como nota: cualquier valor de 2023 para el consumo final o el bruto sería una estimación.

## 4. La brecha, con cifras de un mismo año (2024)

- Ventas de CFE SSB: **225 213 GWh**; suministro calificado: **37 177 GWh**; suma: **262 390 GWh**.
- Consumo final del SEN: **304 011 GWh**. Las ventas de CFE SSB son **74 %** del consumo final, y SSB más calificado, **86 %**.
- Quedan **≈ 41 600 GWh (14 %)** de otras modalidades que entran en el consumo final: contratos de interconexión legados, comercializadores no suministradores, usuarios calificados que participan directamente en el mercado y centros de carga abastecidos de forma remota. **No pude cuantificar cada una por separado**; es el límite de la explicación.

## 5. Consecuencia para la tendencia de la serie

Desde la reforma de 2016 una parte de los usuarios pasa del suministro básico al calificado. Con cifras publicadas: el suministro calificado creció **24.7 %** en 2023 y **27.3 %** en 2024, mientras que las ventas de CFE SSB crecieron **3.9 %** y **1.0 %**. La serie del SIE **subestima el crecimiento del consumo total** y su evolución mezcla demanda real y traspaso de usuarios entre modalidades. Esto matiza las frases de R16 §2.4 sobre la evolución nacional (p. ej. "+27.1 % entre 2006 y 2023"): describen las ventas de CFE SSB, no el consumo del país.

## 6. Texto propuesto (listo para integrar en R15 §2.2 y R16 §2.4)

> **Sobre las series por entidad federativa.** La serie anual por entidad que publica el Sistema de Información Energética (SIE) bajo el nombre "consumo de energía eléctrica" coincide, en el total nacional de 2019 a 2023 y en la variación de 2023 de las 32 entidades, con las ventas de CFE Suministro Básico que reporta la Secretaría de Energía [33]. A partir de esa coincidencia se **infiere** —no hay una definición oficial de la tabla en la información consultada— que representa la energía vendida por el suministrador de servicios básicos, y por ello en este trabajo se denomina "ventas de electricidad de CFE Suministro Básico". No equivale al consumo final del Sistema Eléctrico Nacional, que además incluye el suministro calificado, los contratos de interconexión legados y los centros de carga abastecidos de forma remota [30]. En 2024, las ventas de CFE Suministro Básico fueron 225 213 GWh [35], el suministro calificado 37 177 GWh [35] y el consumo final del sistema 304 011 GWh [30]. Como una parte de los usuarios ha migrado del suministro básico al calificado, la serie subestima el crecimiento del consumo total. Las figuras 2.1, 2.2 y 2.5 deben leerse con esta cobertura.

## 7. Decisiones del autor (2026-10-22) y su aplicación

| # | Decisión | Aplicación |
|---|---|---|
| 1 | Renombrar las Figs. 2.1, 2.2 y 2.5 como ventas de CFE Suministro Básico cuando sea la variable representada | Hecho en `figuras_cap2/` (nombres `Fig2_1_Ventas_CFE_SSB_por_entidad.png`, `Fig2_2_Ventas_CFE_SSB_nacional.png`, `Fig2_5_Ventas_SSB_vs_Generacion.png`), con nota de cobertura en el pie: la identificación se verificó para 2019–2023; en 2006–2018 se **asume** la misma definición y la nota lo dice. Las Figs. 2.3 y 2.4 son generación y no cambian |
| 2 | Presentar la identificación como inferencia respaldada por coincidencias numéricas | §1 y §6 de este documento; la leyenda de las figuras dice "identificación inferida" |
| 3 | Preferir cifras publicadas sobre estimaciones derivadas | §3–§5: comparación con 2024 y 2023 publicadas; las estimaciones derivadas se retiraron del texto |
| 4 | Revisar si figuras, objetivos, metodología o conclusiones confunden ventas de suministro básico con consumo total | `H26_revision_uso_de_consumo.md` |
| 5 | Referencias [33] y [34] con datos verificables | §8 |

## 8. Referencias (numeración propuesta; ver H23)

Solo se consignan campos verificados en los documentos; los campos que no pude comprobar se omiten y se listan debajo.

```latex
\bibitem{SENER_InformePormenorizado2023} Secretaría de Energía (2024). \emph{Informe pormenorizado sobre el desempeño y las tendencias de la industria eléctrica nacional 2023}. Primera edición. Ciudad de México. https://www.gob.mx/cms/uploads/attachment/file/972693/Informe_Pormenorizado_2023.pdf (consultado el 21 de octubre de 2026).
\bibitem{CFE_Reporte4T2023} Comisión Federal de Electricidad. \emph{Información financiera trimestral, consolidado, clave de cotización CFE, cuarto trimestre de 2023}. https://www.cfe.gob.mx/finanzas/reportes-financieros/Reportes\%20Trimestrales\%20Documentos/Reporte\%204Q\%202023.pdf (consultado el 21 de octubre de 2026).
\bibitem{SENER_InformePormenorizado2024} Secretaría de Energía (2025). \emph{Informe pormenorizado sobre el desempeño y las tendencias de la industria eléctrica nacional 2024}. Primera edición. Ciudad de México. https://www.gob.mx/cms/uploads/attachment/file/1072207/Informe_Pormenorizado_sobre_el_Desempe_o_y_las_Tendencias_de_la_Industria_El_ctrica_Nacional_2024.pdf (consultado el 22 de octubre de 2026).
```

| N.º | Qué respalda | Qué **no** se pudo verificar |
|---|---|---|
| [33] SENER, Informe Pormenorizado 2023 | §4.1.1, Tablas 29–31, §4.2, Gráfico 42 (ventas de CFE SSB, por entidad, suministro calificado, consumo neto) | El título exacto de la portada (es una imagen): se tomó de la frase de la introducción ("informe pormenorizado del año 2023 sobre el desempeño y las tendencias de la industria eléctrica nacional") y del nombre del archivo; confirmar. El año 2024 es el de la primera edición según el aviso de derechos; la fecha interna del archivo (enero de 2025) no se usa. No se consigna número de páginas ni ISBN |
| [34] CFE, reporte 4T 2023 | Generación bruta 2023 = 253 265.116 GWh (incluye PIE), igual a la serie del SIE | Fecha de publicación (el PDF trae metadatos de 2016 que no corresponden); dependencia emisora exacta del formato; por eso solo se cita la empresa, el nombre del documento y el periodo |
| [35] SENER, Informe Pormenorizado 2024 (nueva, necesaria para las cifras de 2024) | §4.1.1 (ventas de CFE SSB 2024 = 225 213 GWh), §4.2 (suministro calificado 2024 = 37 177 GWh), consumo neto 2024 | Título exacto de la portada (se tomó del listado de gob.mx); año 2025 = primera edición según el aviso de derechos |
| [30] (existente) | Consumo final 2024 = 304 011 GWh (§2.1.1) y consumo bruto 2024 = 359 807 GWh (§2.1.4) | La fecha de publicación en el DOF (R15); el texto se leyó en una copia del capítulo 2 |

## 9. Qué **no** está demostrado

1. La definición oficial de la tabla del SIE (solo hay identificación numérica) y que la correspondencia valga **antes de 2019** (la nota de Luz y Fuerza del Centro es coherente, no concluyente).
2. El desglose de las ≈ 41.6 TWh de otras modalidades en 2024.
3. Que el consumo final de 2023 sea comparable (no se publica en las fuentes consultadas).
4. La confirmación del SIE o de SENER: queda como acción posible (consulta formal) si el autor quiere citar la definición oficial.
