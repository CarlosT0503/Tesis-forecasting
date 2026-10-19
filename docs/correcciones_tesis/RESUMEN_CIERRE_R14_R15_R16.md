# Resumen de cierre — R14, R15 y R16

Fecha: 2026-10-18. Ninguno está integrado en `tesis.tex` (estado: **Redacción preparada**).

| Obs. | Archivo | Qué quedó resuelto | Qué no pudo demostrarse |
|---|---|---|---|
| **R14** | `R14_cierre_procedencia_y_procesamiento.md` (+ `R14_fuentes_datos.md` para exógenas) | Tabla definitiva de las 8 series (fechas, observaciones, duplicados, horas faltantes); reportes confirmados **Por Balance**; **BCA (H15)** explicado (filas de `Sistema = BCS` con `Area = BCA` desde 2020); **versión de liquidación (H14)**: se usa la de mayor número con datos (4 320/4 320 comparaciones de una muestra de 540 días) y las semanas de prueba son liquidación 0 (L0 vs final ≈ 0.2 %); los 72 archivos de otro formato no afectan (576/576) | El script original de construcción **no se encontró**: la unión por concatenación y la regla "versión más reciente al descargar" son *inferidas*. La verificación es por muestra (1 de cada 5 días), no sobre los 2 700 |
| **R15** | `R15_generacion_consumo_demanda.md` | Definiciones de generación, consumo final (SENER), demanda real y sus dos métodos (CENACE), MW vs MWh; **ecuación del balance** $D = G + I - E + N$ con signos, verificada numéricamente (residuo máximo 10⁻⁵ MWh en 4 232 comparaciones; $N$ suma 0 en el SIN cada hora) | Fecha de publicación en el DOF del Plan de SENER (firmado 14-oct-2025) no aparece en el texto consultado. La página de CENACE no da unidades. Falta decidir "consumo" vs "demanda" en el título |
| **R16** | `R16_contexto_sistema_electrico.md` | Capacidad instalada **93 788 MW verificada** en PRODESEN (Cuadro 4.1, p. 96); generación 351 695 GWh y 24.32 % limpia (p. 97); 8 Gerencias de Control Regional (DOF 2018) ↔ 8 regiones del estudio; importaciones/exportaciones 2023-2024 calculadas de los datos (0.6–0.9 % de la generación) | **No pude reverificar las cifras de INEGI** (582 centrales, 311 411 035 MWh, desglose): la página es dinámica; se usan como aportadas y contrastadas por el autor. Sin desglose completo por tecnología (la Figura 4.9 de PRODESEN es imagen) |

## Hallazgos nuevos (en `HALLAZGOS_PENDIENTES.md`)
- **H16:** BCS existe en los reportes desde 2020 (`Sistema = BCS`); la frase "no se encontró serie reciente" probablemente nace del etiquetado.
- **H17:** el SIN tiene 7 regiones, no 9 (Cap. 2, p. 8); BCA y BCS son sistemas aparte.
- **H18:** las columnas de 2019 no son comparables con 2020+ (la identidad se cumple sin intercambio entre gerencias).
- **H14/H15** pasan a *Resuelto*.

## Archivos creados o modificados
Creados: `R14_cierre_procedencia_y_procesamiento.md`, `R15_generacion_consumo_demanda.md`, `R16_contexto_sistema_electrico.md`, `RESUMEN_CIERRE_R14_R15_R16.md`, `scripts/verificar_procedencia_series.py`.
Modificados: `SEGUIMIENTO.md`, `HALLAZGOS_PENDIENTES.md`, `R14b_procedencia_series_regionales.md` (marcado como superado).

## Para integrar en la tesis
Orden sugerido en el Cap. 2: §2.1 Fuentes (R14 + `R14_fuentes_datos.md`) → §2.2 Generación, consumo y demanda (R15) → §2.3 El sistema eléctrico mexicano (R16). Antes de integrar: confirmar las cifras de INEGI, completar las referencias [24] (INEGI/IGAE) y [25] (temperatura), y decidir H16/H17.
