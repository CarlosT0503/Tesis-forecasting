# R15 — Generación, consumo y demanda

| Campo | Contenido |
|---|---|
| **Observación que resuelve** | R15 (Roberto): "¿Qué es generación, qué es consumo?" |
| **Estado** | Redacción preparada (2026-10-18). **No integrada** en `tesis.tex`. |
| **Ubicación propuesta** | Cap. 2, nueva §2.2 "Generación, consumo y demanda" (después de §2.1 Fuentes, antes de la descripción por entidad federativa). Se propone unificar el término de la variable pronosticada como **demanda real (por balance)**; el título de la tesis dice "consumo". |
| **Qué se evitó** | No se atribuye a CENACE ninguna definición que su página no da (unidades, "consumo final"); esas salen de SENER. |

## Texto propuesto (listo para integrar)

### 2.2. Generación, consumo y demanda

Estos tres términos se usan con frecuencia como sinónimos, pero designan magnitudes distintas.

**Potencia y energía.** La potencia se mide en watts (W; aquí megawatts, MW) y es una tasa instantánea de producción o uso de electricidad. La energía es la potencia acumulada en el tiempo y se mide en watts-hora (aquí megawatts-hora, MWh): una potencia constante de 1 MW durante una hora equivale a 1 MWh. Los reportes de CENACE usados en esta tesis registran **energía por hora** (MWh); como el intervalo es de una hora, esa cifra coincide numéricamente con la potencia media de esa hora (MWh/h), la unidad con que la Secretaría de Energía expresa la demanda máxima integrada [30]. No debe confundirse con la capacidad instalada, que es potencia (MW), ni con la energía anual, que se expresa en GWh o TWh.

**Generación eléctrica.** Es la energía producida por las centrales eléctricas en un periodo. En los reportes diarios aparece como `Generacion (MWh)`, por región y por hora.

**Consumo final.** La Secretaría de Energía lo define como la energía utilizada por los diferentes usuarios de la industria eléctrica; para obtenerlo se considera la energía comercializada en el Sistema Eléctrico Nacional por el suministro básico y el suministro calificado, más la energía entregada a centros de carga abastecidos de manera remota [30]. Es una magnitud **anual** de ventas a usuarios; en 2024 fue de 304 011 GWh [30]. El mismo documento distingue el **consumo bruto** (la totalidad de la energía que resulta de las ventas del suministro y el balance neto entre importaciones y exportaciones; 359 807 GWh en 2024) y señala que las pérdidas técnicas y no técnicas resultan de restar la energía consumida de la entregada a la red (12.3 % del consumo neto del SEN en 2024) [30].

**Demanda real.** Según CENACE, la demanda real del sistema es la energía horaria utilizada en el Sistema Eléctrico Nacional en un día de operación y corresponde al consumo neto de energía [31]. CENACE la estima por dos métodos: **por balance**, con base en la generación neta inyectada al sistema en cada hora, menos la energía de exportación, e incluyendo las pérdidas técnicas y no técnicas; y **por retiros**, agregando todas las compras de energía de las Entidades Responsables de Carga, incluidas las exportaciones y sin las pérdidas de la red del Mercado Eléctrico Mayorista [31]. Estas estimaciones sirven de base para liquidar las transacciones del mercado y se publican por día de operación, con liquidaciones sucesivas [31]. **Los datos de esta tesis corresponden al método por balance** (los reportes se titulan *Estimación de la Demanda Real del Sistema – Por Balance*).

**Importación, exportación e intercambio neto.** Los reportes por región incluyen la energía de importación y de exportación (`Importacion Total`, `Exportacion Total`; en 2019, `Flujo Real de Importacion/Exportacion`) y el *intercambio neto entre gerencias*, la energía que una región recibe (signo positivo) o entrega (signo negativo) respecto de las demás regiones del SIN.

**Ecuación del balance regional.** Para la región *r* y la hora *h*, los reportes verifican

$$D_{r,h} \;=\; G_{r,h} \;+\; I_{r,h} \;-\; E_{r,h} \;+\; N_{r,h}$$

donde *D* es la `Estimacion de Demanda por Balance (MWh)`, *G* la generación, *I* la importación, *E* la exportación y *N* el intercambio neto entre gerencias (positivo si la región recibe energía de otras; en Baja California, que no pertenece al SIN, el reporte no trae este término y se toma *N* = 0). Dentro del SIN, *N* suma cero en cada hora, de modo que a escala del SIN *D* = *G* + *I* − *E*.

**No son magnitudes equivalentes.** La demanda de una región no es su generación: depende de cuánta energía importa o recibe de otras regiones. En 2023, por ejemplo, la región Central generó 36.5 TWh pero tuvo una demanda de 58.6 TWh, mientras que la región Noreste generó 93.4 TWh y demandó 61.8 TWh. Tampoco es el consumo final: la demanda por balance incluye las pérdidas de la red, y el consumo final se mide como energía vendida a usuarios; en 2024 la suma de la demanda de las ocho regiones del estudio fue de 348.5 TWh, frente a un consumo final de 304.0 TWh en el SEN [30], cifras del mismo orden una vez consideradas las pérdidas (12.3 %), pero que no son idénticas porque difieren su cobertura (el estudio no comprende Baja California Sur ni Mulegé, por delimitación del alcance) y su definición.

## Verificación numérica de la ecuación (contra los reportes originales)

Muestra sistemática de 540 días (uno de cada cinco, 2019–2026) × 8 regiones, versión de mayor número con datos (`scripts/verificar_procedencia_series.py`):

| Formato del reporte | Comparaciones (día-región) | Máximo \|*G* + *I* − *E* + *N* − *D*\| (MWh) | Media (MWh) |
|---|---|---|---|
| 2020 en adelante (con `Intercambio neto`) | 3 736 | 1.0 × 10⁻⁵ | 1.1 × 10⁻⁶ |
| 2019 (`Flujo Real`, sin `Intercambio neto`) | 496 | 1.8 × 10⁻¹² | 5.2 × 10⁻¹⁴ |

La identidad se cumple a la precisión del redondeo en las ocho regiones. Comprobaciones adicionales en tres días (2021-03-17, 2023-07-12, 2025-02-10): la suma horaria del intercambio neto sobre las siete regiones del SIN es 0.000 MWh, y la suma de *G* + *I* − *E* de esas regiones coincide con la suma de *D* (p. ej., 2023-07-12: 1 060 104 + 2 465 − 6 136 = 1 056 433 MWh). Regiones netamente receptoras en esos tres días: Central, Occidental y Peninsular; netamente exportadoras: Noreste, Oriental, Noroeste y Norte (Noroeste y Norte con saldo menor).

Totales anuales 2023 de las ocho regiones del estudio (suma de las series procesadas; **no** incluye Baja California Sur ni Mulegé): generación 343.1 TWh, importación 2.1 TWh, exportación 3.1 TWh y demanda 342.0 TWh (343.1 + 2.1 − 3.1 = 342.0). Para 2024: 348.8, 2.5, 2.8 y 348.5 TWh.

## Notas y límites

- La página de CENACE **no especifica unidades**; el MWh viene de los encabezados de los archivos (`(MWh)`).
- "Consumo final" no es una definición de CENACE: se toma de SENER [30].
- En los reportes de 2019 la identidad se cumple **sin** el término *N* y con importaciones/exportaciones nulas en varias regiones del SIN, es decir, la columna `Generacion` de 2019 no es comparable con la de 2020 en adelante para las regiones del SIN. No afecta a los experimentos (usan 2025–2026) pero sí a cualquier análisis de 2019.
- [30] se firmó el 14 de octubre de 2025; su fecha exacta de publicación en el DOF no aparece en el texto consultado (verificar).
- Pendiente de decidir: unificar "consumo" (título y Cap. 2) con "demanda" (variable pronosticada).

## Referencias

- **[31]** CENACE, *Estimación de la Demanda Real*, Sistema de Información del Mercado. <https://www.cenace.gob.mx/Paginas/SIM/Reportes/EstimacionDemandaReal.aspx> (consultada el 2026-10-18). Es una entrada **nueva**: la [20] existente es otra página de CENACE (*Energía Generada por Tipo de Tecnología*).
- **[30]** Secretaría de Energía, *ACUERDO por el que la Secretaría de Energía emite el Plan de Desarrollo del Sector Eléctrico* (con el Plan de Desarrollo del Sector Eléctrico 2025-2039), firmado el 14 de octubre de 2025, Diario Oficial de la Federación. <https://sidof.segob.gob.mx/notas/docFuente/5770297> (consultada el 2026-10-18). Definiciones de consumo final, consumo bruto, pérdidas y demanda (MWh/h); cifras de 2024.

## Revisión de consistencia (2026-10-20)

Se revisaron los usos de "generación", "consumo" y "demanda" en R14, R15 y R16. **No se cambió el título de la tesis** (decisión del autor pendiente).

| # | Hallazgo | Acción |
|---|---|---|
| 1 | **Término de la variable pronosticada.** El título dice "Consumo Eléctrico"; la Introducción (§0.3.1) dice "demanda eléctrica" y R14/R15 usan "demanda real (por balance)". El Cap. 2 usa "consumo" para la serie anual del SIE por entidad. Son tres magnitudes distintas con dos palabras. | Mantener "demanda" para la serie horaria pronosticada y "consumo" solo para la serie anual del SIE. Decidir con el autor si el título se ajusta; **no tocado**. |
| 2 | **Cobertura del "consumo" del SIE sin verificar.** La tabla del SIE da 222.9 TWh de consumo nacional en 2023; SENER [30] da 304.0 TWh de *consumo final* en 2024. Una diferencia de ≈ 36 % no se explica por el cambio de año (el consumo del SIE creció en promedio 1.4 % anual entre 2006 y 2023), así que las dos series no miden lo mismo o no cubren lo mismo. No se pudo comprobar qué incluye la tabla del SIE (su fuente es el Anexo Estadístico del Informe de Gobierno). | No equiparar el consumo del SIE con el consumo final de SENER. Ver H26. En R16 §2.4 se ajustó la frase que los igualaba. |
| 3 | **BCS y Mulegé.** R15 decía "el estudio excluye Baja California Sur y Mulegé" (sugería una exclusión técnica). | Reformulado como delimitación del alcance (H16). |
| 4 | **Comparación demanda de las ocho regiones vs consumo final nacional.** La cifra 348.5 TWh (demanda 2024, ocho regiones) frente a 304.0 TWh (consumo final, SEN) se explica en parte por pérdidas (12.3 %), pero el cálculo no cierra exactamente; el texto ya dice "no son idénticas". | Sin cambio; no afirmar que concilian. |
