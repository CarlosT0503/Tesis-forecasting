# R16 — Contexto del sistema eléctrico mexicano (versión 2, ampliada)

| Campo | Contenido |
|---|---|
| **Observación que resuelve** | R16 (Roberto): "Contexto, de dónde proviene la energía eléctrica de México, cuántas plantas hay, se compra al exterior…" (más R15 en lo que toca a las figuras) |
| **Estado** | Redacción preparada, versión 2 (2026-10-19), **actualizada el 2026-10-20**: figuras 2.1, 2.2, 2.4 y 2.5 regeneradas en `figuras_cap2/` y Baja California Sur redactada como delimitación del alcance (H16). **No integrada** en `tesis.tex`. Sustituye a la versión 1 (breve). |
| **Figuras nuevas** | `docs/correcciones_tesis/figuras_cap2/` (PNG + `datos_fig2_*.csv`), generadas con `scripts/generar_figuras_cap2.py`. **No sobrescriben las originales.** La Fig. 2.3 no se regeneró (ver Parte A2). |
| **Ubicación propuesta** | Cap. 2, tres secciones nuevas después de §2.2 (R15): **§2.3** El sistema eléctrico en cifras; **§2.4** Consumo y generación por entidad federativa (comenta las Figuras 2.1–2.5 en una sola narrativa); **§2.5** Organización regional, intercambios y demanda regional; **§2.6** Implicaciones para el pronóstico (breve). Reemplaza la frase actual "el SIN se divide en nueve regiones" (H17). |
| **Datos de respaldo** | `docs/correcciones_tesis/datos_cap2/*.csv`, generados por `scripts/verificar_figuras_cap2.py` (solo lectura sobre los CSV del SIE y las series procesadas). |
| **Convención de citas** | Número entre corchetes pegado a cada dato: [20] CENACE (ya en la bibliografía); [21] SIE (ya); **nuevas** [26]–[32], listadas al final con su `\bibitem`. El cálculo propio se marca "(cálculo propio con [x])". |

---

## Parte A — Diagnóstico de las figuras actuales del Capítulo 2

Las cinco figuras (`tesis.tex`, líneas 111–145; PDF pp. 5–7) provienen de dos tablas del SIE [21]: *Consumo de energía eléctrica por entidad federativa* (anual, GWh) y *Generación bruta de CFE más PIE's por entidad federativa* (mensual, MWh). Se recalcularon todas las cifras (Parte C).

| Fig. | Qué muestra realmente | Fuente | Patrón verificado | Problema detectado | Cambio propuesto |
|---|---|---|---|---|---|
| **2.1** Consumo promedio por entidad | Promedio **anual** 2006–2024 (GWh/año) por estado | SIE, consumo [21,27] | Estado de México 16.5 y Nuevo León 16.5 TWh/año; CDMX 13.0; Jalisco 12.2; Chihuahua 11.1. Menores: Campeche 1.2, Nayarit 1.4, Tlaxcala 1.7. Coincide con el texto | El título interno dice "desde Enero/2001"; la serie empieza en **2006** y es anual. El promedio incluye 2024 incompleto (hasta junio): baja cada media entre 1.6 % y 3.2 % respecto de 2006–2023 y solo intercambia dos pares de entidades casi iguales (Baja California/Sonora y Chiapas/Guerrero) | **Hecho:** título con el periodo real y nota sobre 2024 parcial (`Fig2_1_…png`) |
| **2.2** Consumo total | Consumo nacional anual 2006–2024 (GWh) | SIE, consumo [27] | 175.4 TWh (2006) → 222.9 (2023), +27.1 %; 2020: −5.6 %; 2021: sin cambio (−0.01 %); 2023: +7.9 % sobre 2021 | **(a)** El archivo que genera la figura (`Diferencias Energia por Año.ipynb`) usa una lista escrita a mano marcada "Datos ficticios similares a la gráfica original" (difieren hasta ≈ 1.2 % de los totales del SIE) y etiqueta el eje en kWh. **(b)** 2024 es un **año incompleto** ("Cifras al mes de junio 2024", 106.9 TWh = 47.9 % de 2023): la "reducción" no es una caída del consumo | **Regenerar** la figura con los totales exactos del SIE y marcar 2024 como parcial (o excluirlo). Reescribir el texto: no hay reducción en 2024 |
| **2.3** Generación anual | Generación bruta anual 2006–2024 (MWh), **solo CFE + PIE** | SIE, generación [26,21] | 223.6 TWh (2006) → máx. 261.7 (2016) → 250.4 (2019) → 224.6 (2020, −10.3 %) → 224.2 (2021) → 253.2 (2023) → 257.8 (2024, 12 meses completos, **+1.8 %**) | El texto dice que la reducción de 2024 "también puede apreciarse en la Figura 2.3": **no es así**, la generación de 2024 sube. La caída de 2020 es casi el doble de la del consumo y la serie solo cubre CFE+PIE | Corregir el texto (ver §2.4); conservar la figura y añadir la nota de cobertura |
| **2.4** Generación promedio por entidad | Promedio **mensual** (MWh/mes), ene-2002 a dic-2024 | SIE, generación [26] | Veracruz 2.86, Tamaulipas 2.26, Guerrero 1.39 millones de MWh/mes. Menores: Quintana Roo 0.017, CDMX 0.036, Jalisco 0.10. Los tres mayores suman 32.5 % del total estatal | Mezcla de unidades con la Fig. 2.1 (anual vs mensual); título "desde Enero/2001" (la serie empieza en 2002); cuatro estados (Aguascalientes, Tabasco, Tlaxcala, Zacatecas) no aparecen en la tabla | Expresar en GWh/año (comparable con 2.1) y corregir el título; anotar los cuatro estados sin registro |
| **2.5** Consumo vs. generación | Barras = consumo; rombos = generación, por estado | SIE [26,27] | Con unidades homogéneas (GWh/año, media 2006–2023): generación/consumo = 5.9 (Colima), 5.7 (Guerrero), 4.5 (Chiapas), 3.4 (Tamaulipas), 3.3 (Veracruz); 0.04 (CDMX y Quintana Roo), 0.11 (Jalisco), 0.40 (Edo. de México) | **No pude reproducir la escala del gráfico**: los rombos de generación coinciden con la Fig. 2.4 (MWh/**mes**) pero las barras de consumo equivalen a ≈ la sexta parte del consumo **anual** (estimación leyendo el gráfico), no a la doceava. En unidades homogéneas **San Luis Potosí no es "equilibrado"** (genera 1.7 veces su consumo); Oaxaca sí (1.05) | Regenerar con ambas magnitudes en GWh/año y cambiar el ejemplo de equilibrio (Oaxaca, Baja California Sur 1.04, Campeche 1.03) |

**Orden y títulos.** Se propone conservar el orden 2.1 → 2.5 (primero consumo, luego generación, luego su comparación) y solo (i) regenerar 2.2 y 2.5, (ii) corregir los títulos de 2.1 y 2.4 y (iii) añadir a todas las leyendas el periodo y la unidad. Todo está justificado por los problemas de la tabla.

### Parte A2 — Figuras regeneradas (2026-10-20)

Archivos en `docs/correcciones_tesis/figuras_cap2/`; los datos de cada una, en `datos_fig2_*.csv`. Las imágenes originales no se tocaron.

| Archivo | Título propuesto (periodo real) | Decisión de comparabilidad |
|---|---|---|
| `Fig2_1_Consumo_promedio_por_entidad.png` | Consumo anual promedio por entidad federativa, 2006–2024 | Mismo cálculo que la original; nota al pie: 2024 incluye solo enero–junio. |
| `Fig2_2_Consumo_anual_nacional.png` | Consumo eléctrico nacional, 2006–2024 | 2024 se conserva como **rombo hueco naranja** con línea punteada y la anotación "enero–junio, no comparable con años completos"; la serie de años completos va aparte. El eje X muestra solo años enteros. |
| `Fig2_4_Generacion_promedio_por_entidad.png` | Generación bruta anual promedio por entidad federativa, 2002–2024 (CFE + PIE) | Ahora en GWh/año (la original era MWh/mes), comparable con la Fig. 2.1. Morelos va rayado (datos solo desde marzo de 2017). |
| `Fig2_5_Consumo_vs_Generacion.png` | Consumo y generación eléctrica promedio por entidad federativa, 2006–2023 | Ambas magnitudes en GWh/año; se promedian solo años completos (2006–2023). **27 entidades con cobertura comparable.** Se muestran sin comparar: Tlaxcala, Zacatecas, Aguascalientes y Tabasco (sin fila de generación en la fuente) y Morelos (cobertura incompleta). |

La **Fig. 2.3** (generación anual nacional) no se regeneró porque no se pidió; su corrección se limita al texto de §2.4.

---

## Parte B — Texto propuesto (listo para integrar)

### 2.3. El sistema eléctrico mexicano en cifras

**Centrales y tecnologías.** En 2023, México contó con 582 centrales eléctricas que generaron 311 411 035 MWh, según el INEGI [29]. De esa energía, 216 758 822 MWh (69.6 %) fueron termoeléctricas, 33 486 589 MWh (10.8 %) eoloeléctricas y 20 901 156 MWh (6.7 %) hidroeléctricas [29]; el 12.9 % restante (40 264 468 MWh) corresponde a las demás tecnologías y se obtuvo por diferencia (cálculo propio con [29]). Estos porcentajes tienen como denominador la cifra del INEGI y no se combinan con los de otras fuentes.

**Una segunda fuente, otra cobertura.** El Programa de Desarrollo del Sistema Eléctrico Nacional (PRODESEN) 2024–2038, de la Secretaría de Energía, estima para 2023 una generación total equivalente de 351 695 GWh —cifra que incluye 5 191 GWh de generación distribuida fotovoltaica—, de la cual 24.32 % provino de energías limpias y 75.68 % de energías fósiles [28, p. 97]. La diferencia con la cifra del INEGI (351.7 frente a 311.4 TWh) refleja coberturas y definiciones distintas —el PRODESEN reporta el Sistema Eléctrico Nacional más la generación distribuida—, que ninguna de las dos fuentes concilia; por eso en esta tesis se citan por separado. En el mismo año hubo una sequía: la generación hidroeléctrica se redujo 42 % respecto de 2022 y 40.6 % respecto de 2021 [28, p. 97].

**Capacidad instalada frente a generación efectiva.** La capacidad instalada neta del país en 2023 fue de 93 788 MW: 90 447 MW de capacidad interconectada, incluidas centrales en pruebas, y 3 341 MW de generación distribuida [28, Cuadro 4.1, p. 96]. La capacidad es una potencia máxima disponible; la generación, la energía efectivamente producida. Si las centrales operaran todo el año a plena capacidad (93 788 MW × 8 760 h) producirían unos 822 TWh; la generación de 351.7 TWh equivale a un factor de planta medio implícito de ≈ 43 % (cálculo propio con [28]; es un promedio de tecnologías muy distintas y mezcla capacidad con centrales en pruebas). Esa brecha obedece, entre otras razones, a la intermitencia de las fuentes renovables, al despacho según la demanda y al estado de los embalses; en un año seco como 2023 la generación hidroeléctrica cayó, como se indicó. Para el pronóstico de demanda lo relevante es que la capacidad no limita el consumo observado en el horizonte de esta tesis, pero sí condiciona cómo se cubre.

**Cuatro magnitudes, cuatro coberturas.** Para evitar confusiones, la Tabla 2.A resume las cifras de generación de 2023 que se usan en el capítulo.

*Tabla 2.A. Cifras de generación de 2023 y su cobertura.*

| Fuente | Cifra | Qué cubre |
|---|---|---|
| PRODESEN 2024–2038 [28] | 351 695 GWh | Sistema Eléctrico Nacional más generación distribuida |
| INEGI [29] | 311 411 035 MWh (311.4 TWh) | 582 centrales eléctricas |
| SIE, generación bruta [26] | 253.2 TWh (cálculo propio con [26]) | Solo CFE y productores independientes (PIE), por entidad federativa |
| Series de CENACE usadas en esta tesis [31] | 343.1 TWh (cálculo propio con [31]) | Ocho regiones de control; sin Baja California Sur ni Mulegé |

### 2.4. Consumo y generación por entidad federativa

Las Figuras 2.1 a 2.5 describen, con datos del SIE [21], cómo se reparten el consumo y la generación entre las entidades federativas. Conviene precisar sus unidades y coberturas. El consumo es una serie **anual** en GWh, de 2006 a 2024, con cifras de 2024 solo hasta junio [27]; la generación es una serie **mensual** en MWh, de enero de 2002 a marzo de 2025, correspondiente a la generación bruta de CFE más los PIE [26]. Se usan los datos hasta diciembre de 2024 para la generación.

**Concentración del consumo.** La Figura 2.1 muestra el consumo anual promedio por entidad. El Estado de México y Nuevo León, con 16.5 TWh por año cada uno, encabezan la lista, seguidos de la Ciudad de México (13.0 TWh) y Jalisco (12.2 TWh); Campeche (1.2 TWh), Nayarit (1.4 TWh) y Tlaxcala (1.7 TWh) registran los menores valores (cálculo propio con [27]). Las tres primeras entidades concentran el 23.2 % del consumo estatal y las cinco primeras el 34.9 % (promedio 2006–2023; el promedio de 2006–2024 de la figura incluye 2024 solo hasta junio, lo que reduce cada valor entre 1.6 % y 3.2 % sin alterar la lectura). La magnitud del consumo difiere, así, en un orden de magnitud entre entidades.

**Evolución nacional del consumo y de la generación.** La Figura 2.2 presenta el consumo nacional. Entre 2006 y 2023 pasó de 175.4 a 222.9 TWh (+27.1 %, alrededor de 1.4 % anual); en 2020 cayó 5.6 % respecto de 2019, en 2021 se mantuvo prácticamente sin cambio y en 2023 superó en 7.9 % el nivel de 2021 [27]. El valor de 2024 (106.9 TWh) **no representa una caída**: equivale al 47.9 % de 2023 porque la fuente declara cifras "al mes de junio de 2024" [27]; no debe interpretarse como reducción del consumo anual. La Figura 2.3 muestra la generación nacional de CFE y PIE: creció de 223.6 TWh en 2006 a un máximo de 261.7 TWh en 2016, bajó a 250.4 TWh en 2019, cayó 10.3 % en 2020 (224.6 TWh) y se mantuvo en 224.2 TWh en 2021; se recuperó hasta 253.2 TWh en 2023 y 257.8 TWh en 2024, año que sí tiene sus doce meses [26]. Ambas series coinciden, por tanto, en un descenso en 2020, pero con distinta magnitud (−5.6 % en consumo y −10.3 % en generación), y la generación no muestra reducción en 2024. Como la serie de generación cubre solo CFE y PIE, su caída de 2020–2021 no puede atribuirse únicamente a un cambio en la demanda: para ese año no se comparó con una serie de cobertura completa.

**Distribución de la generación.** La Figura 2.4 presenta la generación bruta anual promedio por entidad (2002–2024, GWh por año, la misma unidad que la Figura 2.1). Veracruz (34 303 GWh), Tamaulipas (27 148 GWh) y Guerrero (16 683 GWh) encabezan la lista y suman el 32.6 % de la generación estatal; Quintana Roo (202 GWh), la Ciudad de México (437 GWh) y Jalisco (1 195 GWh) registran los menores valores entre las entidades con cobertura completa [26] (cálculo propio). Morelos aparece con un promedio de 719 GWh, pero la fuente solo tiene datos desde marzo de 2017 (en la figura va rayado) y su valor no es comparable. Cuatro entidades —Aguascalientes, Tabasco, Tlaxcala y Zacatecas— no figuran en la tabla del SIE; su ausencia indica falta de registro en esa serie, no necesariamente ausencia de generación.

**Desajuste entre generación y consumo.** La Figura 2.5 compara ambas magnitudes. Expresadas en la misma unidad (GWh por año, promedio 2006–2023), la generación supera varias veces al consumo en Colima (5.9), Guerrero (5.7), Chiapas (4.5), Tamaulipas (3.4) y Veracruz (3.3), mientras que en la Ciudad de México y Quintana Roo es solo el 4 % y en Jalisco el 11 % (cálculo propio con [26] y [27]); en el otro extremo, Oaxaca (1.05), Baja California Sur (1.04) y Campeche (1.03) presentan un comportamiento equilibrado. La comparación incluye las 27 entidades que tienen generación registrada con cobertura completa en 2006–2023; Morelos (datos solo desde marzo de 2017) y las cuatro entidades sin registro (Aguascalientes, Tabasco, Tlaxcala y Zacatecas) se muestran únicamente con su consumo. Este desajuste geográfico implica que la energía debe transportarse entre entidades y regiones. No es un balance físico exacto: la generación bruta de CFE y PIE y el consumo anual del SIE [27] son magnitudes distintas, como se explicó en la sección 2.2. La cobertura exacta del consumo del SIE no se pudo contrastar con el consumo final de la Secretaría de Energía [30] (ver H26), por lo que no se equiparan.

**Síntesis.** Las cinco figuras muestran (i) que el consumo está concentrado en pocas entidades, (ii) que la generación se ubica en otras y (iii) que ambos agregados nacionales respondieron al choque de 2020 con distinta intensidad. De ahí que la operación del sistema, y por tanto esta tesis, se organice por regiones de control y no por entidades.

### 2.5. Organización regional, intercambios y demanda regional

**Operación por regiones.** El Centro Nacional de Control de Energía (CENACE) opera el Sistema Eléctrico Nacional y ejerce sus atribuciones territoriales mediante ocho Gerencias de Control Regional —Baja California, Central, Noreste, Noroeste, Norte, Occidental, Oriental y Peninsular—, además de las gerencias del Centro Nacional y del Centro Alterno [32]; la de Baja California atiende también el estado de Baja California Sur y el municipio de San Luis Río Colorado, Sonora [32]. En los reportes de demanda real [26], la información se presenta por sistema: el Sistema Interconectado Nacional (SIN), con siete regiones (Central, Noreste, Noroeste, Norte, Occidental, Oriental y Peninsular), y los sistemas de Baja California y de Baja California Sur, que no pertenecen al SIN. Las ocho regiones de esta tesis —BCA, CEN, NES, NOR, NTE, OCC, ORI y PEN— coinciden con las ocho Gerencias de Control Regional. El estudio comprende, por tanto, las siete regiones del Sistema Interconectado Nacional y el sistema de Baja California. Baja California Sur es un sistema separado, cuyos registros existen en los reportes de CENACE, pero no forma parte del conjunto de regiones seleccionadas; esta es una delimitación del alcance del trabajo, y su incorporación puede considerarse como una extensión futura.

**Generación regional y demanda regional.** La generación de una región no coincide con su demanda. La Tabla 2.B muestra las cifras de 2023 de las ocho regiones, calculadas a partir de las series de CENACE [31] mediante la identidad del balance (sección 2.2): el intercambio neto es la energía que la región recibe (positivo) o entrega (negativo) respecto de las demás.

*Tabla 2.B. Generación, demanda e intercambios por región, 2023 (TWh).*

| Región | Generación | Importación | Exportación | Demanda | Intercambio neto |
|---|---|---|---|---|---|
| BCA | 15.31 | 1.55 | 0.86 | 16.00 | — |
| CEN | 36.50 | 0.00 | 0.00 | 58.62 | +22.12 |
| NES | 93.37 | 0.48 | 0.08 | 61.76 | −32.01 |
| NOR | 31.55 | 0.00 | 0.00 | 27.61 | −3.93 |
| NTE | 34.04 | 0.00 | 0.00 | 31.18 | −2.86 |
| OCC | 50.61 | 0.00 | 0.00 | 75.53 | +24.92 |
| ORI | 70.23 | 0.05 | 1.74 | 55.39 | −13.15 |
| PEN | 11.46 | 0.00 | 0.43 | 15.94 | +4.91 |

(Cálculo propio con [31]; BCA no pertenece al SIN y no tiene intercambio entre gerencias. En el SIN, el intercambio neto suma cero.) Las regiones Central, Occidental y Peninsular dependen de la energía que reciben de otras (equivalente a 38 %, 33 % y 31 % de su demanda, respectivamente), mientras que Noreste y Oriental entregan más de lo que consumen.

**Importaciones y exportaciones.** Los intercambios con el exterior son pequeños frente a la generación: en las ocho regiones suman 2.1 TWh de importación y 3.1 TWh de exportación en 2023 (0.6 % y 0.9 % de la generación de esas regiones) y 2.5 y 2.8 TWh en 2024 (0.7 % y 0.8 %) [31]. Las importaciones se concentran en Baja California (1.5 TWh en 2023) y en el Noreste (0.5 TWh); las exportaciones, en la región Oriental (1.7 TWh), Baja California (0.9 TWh) y la Peninsular (0.4 TWh). Son cifras anuales calculadas de los 365 días de 2023 (366 de 2024); no se extrapola ningún reporte diario.

### 2.6. Implicaciones para el pronóstico

Las diferencias entre regiones no son solo de tamaño. En 2023 la demanda media horaria de la región Occidental (8 622 MWh/h) fue 4.7 veces la de la Península (1 820 MWh/h) (cálculo propio con [31]). La amplitud estacional también difiere: el cociente entre el mes de mayor y el de menor demanda va de 1.10 en la región Central a 2.16 en la Noroeste; el máximo mensual ocurre en junio (CEN, OCC, ORI), julio (BCA, NOR, NTE, PEN) o agosto (NES), y el mínimo, casi siempre en diciembre. Todos los días de la semana no son iguales: el domingo promedia entre 82 % (OCC) y 93 % (ORI) de un día laborable, y la hora de mayor demanda del reporte varía entre las 17 y las 22 h según la región (Tabla 2.C, cálculo propio con [31]). Estos patrones —ciclo diario, ciclo semanal y estacionalidad anual con amplitud propia de cada región— justifican modelar cada región por separado y usar una ventana semanal de 168 horas.

La literatura citada en esta tesis vincula parte de esa variación con la temperatura [10, 13], y la demanda de cada región recibe además el efecto de la actividad económica local; en los experimentos, sin embargo, la temperatura y el IGAE son series **nacionales** mensuales, de modo que solo pueden explicar la parte común a todas las regiones. Operativamente, la demanda regional que se pronostica es una estimación por balance y, en las semanas de prueba, preliminar (liquidación 0; sección 2.1); el cambio de horario de Baja California introduce días de 23 y 25 horas.

*Tabla 2.C. Patrones descriptivos de la demanda por región, 2023.*

| Región | Mes pico | Mes valle | Máx./mín. mensual | Domingo / día laborable | Hora pico (del reporte) |
|---|---|---|---|---|---|
| BCA | julio | diciembre | 1.81 | 0.85 | 17 |
| CEN | junio | diciembre | 1.10 | 0.87 | 20 |
| NES | agosto | diciembre | 1.70 | 0.84 | 17 |
| NOR | julio | enero | 2.16 | 0.92 | 17 |
| NTE | julio | noviembre | 1.71 | 0.85 | 21 |
| OCC | junio | diciembre | 1.26 | 0.82 | 21 |
| ORI | junio | diciembre | 1.28 | 0.93 | 21 |
| PEN | julio | diciembre | 1.45 | 0.93 | 22 |

(La "hora" es la del reporte: la hora *h* cubre de *h*−1 a *h*.)

---

## Parte C — Tabla de cifras, procedencia y verificación

| Cifra | Valor | Alcance | Fuente y ubicación | Estado |
|---|---|---|---|---|
| Centrales eléctricas 2023 | 582 | Nacional | INEGI [29] | **Aportada por el autor**; no reverificable (página dinámica) |
| Generación 2023 | 311 411 035 MWh | Nacional (582 centrales) | INEGI [29] | idem |
| Termo / eólica / hidro 2023 | 216 758 822 / 33 486 589 / 20 901 156 MWh | Nacional | INEGI [29] | idem; porcentajes calculados aquí |
| Capacidad instalada neta 2023 | 93 788 MW (90 447 + 3 341 GD) | Nacional | PRODESEN 2024–2038, cap. 4, Cuadro 4.1, p. 96 [28] | **Verificada** en el texto del PDF |
| Generación total equivalente 2023 | 351 695 GWh (incl. 5 191 GWh GD-FV); 24.32 % limpia / 75.68 % fósil | SEN + GD | PRODESEN cap. 4, p. 97 [28] | **Verificada** |
| Reducción hidroeléctrica 2023 | −42 % vs 2022; −40.6 % vs 2021 | Nacional | PRODESEN cap. 4, p. 97 [28] | **Verificada** |
| Consumo final 2024 / consumo bruto 2024 | 304 011 / 359 807 GWh | SEN | SENER, Plan 2025–2039 [30] | **Verificada** (texto del DOF) |
| Consumo anual por entidad 2006–2024 | tabla (GWh) | 32 entidades; 2024 hasta junio | SIE [27]; nota "Cifras al mes de junio 2024" | **Verificada** en el archivo |
| Generación mensual por entidad ene-2002 – mar-2025 | tabla (MWh) | 29 entidades + plantas móviles; CFE + PIE | SIE [26] | **Verificada** en el archivo |
| Factor de planta medio implícito | ≈ 43 % | Nacional | Cálculo propio con [28] | Calculado; indicativo |
| Generación vs demanda, intercambios y patrones por región | Tablas 2.B y 2.C | 8 regiones, 2023 | Cálculo propio con [31] | Calculado de los datos |
| 8 Gerencias de Control Regional | 8 + Centro Nacional y Alterno | Nacional | DOF 15-may-2018 [32] | **Verificada** |

## Parte D — Referencias

Entradas en el formato de la bibliografía de la tesis. **[20]** y **[21]** ya existen. Las fechas de consulta son las de esta sesión.

```latex
\bibitem{SIE_Generacion} Secretaría de Energía, Sistema de Información Energética (2025). \emph{Generación bruta de CFE más PIE's por Entidad Federativa (megawatts-hora)}, con información de CFE. Archivo descargado el 18 de julio de 2025. https://sie.energia.gob.mx/inicio//
\bibitem{SIE_Consumo} Secretaría de Energía, Sistema de Información Energética (2025). \emph{Consumo de energía eléctrica por entidad federativa (gigawatts-hora)}; fuente: Anexo Estadístico del Informe de Gobierno, Sexto Informe de Gobierno 2023-2024; cifras al mes de junio de 2024. https://sie.energia.gob.mx/inicio//
\bibitem{CENACE_DemandaReal} CENACE (2026). \emph{Estimación de la Demanda Real}. Sistema de Información del Mercado. https://www.cenace.gob.mx/Paginas/SIM/Reportes/EstimacionDemandaReal.aspx (consultado el 18 de octubre de 2026).
\bibitem{SENER_Plan2025} Secretaría de Energía (2025). \emph{Acuerdo por el que la Secretaría de Energía emite el Plan de Desarrollo del Sector Eléctrico} (Plan de Desarrollo del Sector Eléctrico 2025-2039). Diario Oficial de la Federación. https://sidof.segob.gob.mx/notas/docFuente/5770297
\bibitem{PRODESEN} Secretaría de Energía (2024). \emph{Programa de Desarrollo del Sistema Eléctrico Nacional 2024-2038}, Capítulo 4: Programas Indicativos para la Instalación y Retiro de Centrales Eléctricas. https://base.energia.gob.mx/PRODESEN2024/prodesen24-38cap4.PDF
\bibitem{INEGI_Cuentame} INEGI (2024). \emph{Cuéntame de México: Electricidad}. https://cuentame.inegi.org.mx/explora/economia/electricidad/
\bibitem{CENACE_GCR} Centro Nacional de Control de Energía (2018). \emph{Acuerdo por el que se establece la circunscripción territorial de las Gerencias de Control Regional del Centro Nacional de Control de Energía}. Diario Oficial de la Federación, 15 de mayo de 2018. https://www.cenace.gob.mx/Docs/16_MARCOREGULATORIO/CENACEOrganizacion/(DOF%202018-05-15%20CENACE)%20Circunscripci%C3%B3n%20territorial%20GCR.pdf
```

| N.º | Institución | Documento | Año | Dónde aparece lo citado | Verificación |
|---|---|---|---|---|---|
| [20] | CENACE | *Energía Generada por Tipo de Tecnología* (SIM, generación liquidada) | existente | Reporte mensual de generación intermitente y firme a nivel agregado; la página no define las categorías ni las unidades | Página consultada: **no respalda cifras de este capítulo**; es una referencia de lectura |
| [21] | SENER, SIE | Sistema de Información Energética | existente | Portal de las tablas [26] y [27] | — |
| [26] | SENER, SIE | *Generación bruta de CFE más PIE's por Entidad Federativa* | 2025 | Título, unidades y nota "con información de CFE" en el encabezado y pie del archivo | Verificada en el archivo |
| [27] | SENER, SIE | *Consumo de energía eléctrica por entidad federativa* | 2025 | Encabezado, GWh y notas ("Cifras al mes de junio 2024"; fuente: Anexo Estadístico del Informe de Gobierno) | Verificada en el archivo |
| [28] | SENER | PRODESEN 2024–2038, cap. 4 | 2024 | Cuadro 4.1 (p. 96); texto de §4.2.5 (p. 97) | Verificada en el PDF; la participación por tecnología está en la Figura 4.9 (imagen), **no extraída** |
| [29] | INEGI | *Cuéntame de México: Electricidad* | 2024 | Cifras de 2023 aportadas por el autor | **Pendiente de reverificar** |
| [30] | SENER | Acuerdo y Plan de Desarrollo del Sector Eléctrico 2025–2039 | 2025 | Definición de consumo final, consumo bruto y pérdidas; cifras de 2024 | Verificada; fecha de publicación en el DOF no aparece en el texto consultado |
| [31] | CENACE | *Estimación de la Demanda Real* (reportes diarios "Por Balance") | 2026 | Series procesadas de esta tesis; ver `R14_cierre…` | Verificada (R14) |
| [32] | CENACE | Acuerdo de circunscripción territorial de las GCR | 2018 | Artículo único, fracciones I a IX | Verificada |

(En R14 y R15 la página *Estimación de la Demanda Real* se citó como [20] o [C1]; para no confundirla con la entrada existente [20] se unifica como **[31]**, y el Plan de SENER, antes [S1], como **[30]**.)

## Parte E — Pendientes por verificar

1. **INEGI [29]:** cifras de 2023 aportadas por el autor; no reverificables desde aquí. Conviene citar la tabla exacta (título, fecha de consulta).
2. **Participación por tecnología:** solo hay tres tecnologías (INEGI) y la proporción limpia/fósil (PRODESEN). El desglose completo está en la Figura 4.9 del PRODESEN (imagen) y probablemente en su Capítulo 3, que no se pudo descargar completo.
3. **Mulegé** como cuarto sistema eléctrico: aparece en una presentación de CENACE localizada por búsqueda; no verificada en su texto completo y no incluida.
4. **Figuras 2.2 y 2.5:** ya regeneradas (Parte A2). Falta que el autor las revise y decida si sustituyen a las originales; la Fig. 2.3 sigue sin regenerar. Las figuras nuevas usan fondo oscuro; verificar que el estilo sea coherente con el resto de las figuras de la tesis.
5. **Alcance del "consumo" del SIE (H26):** la serie por entidad (Figs. 2.1, 2.2 y 2.5, §2.4) son las **ventas de CFE Suministro Básico**, no el consumo final del SEN (222.9 frente a ≈ 298.6 TWh en 2023). Antes de integrar, sustituir "consumo" por la denominación elegida por el autor y añadir la nota de cobertura de `H26_discrepancia_SIE_SENER.md` §3; el "+27.1 % entre 2006 y 2023" describe esas ventas y no el consumo del país.
6. **Baja California Sur (H16):** decisión del autor (2026-10-20): su exclusión se presenta como delimitación del alcance, no como falta de datos. Los textos de la tesis que dicen "no se encontró una serie reciente" (§0.3.1, §5.1.1) y los borradores R14 deben reemplazarse por esa redacción. Queda como extensión futura; no se modifican los experimentos.
7. **Causas** de la caída de 2020–2021 en generación y consumo: no se afirman; la tesis no las analiza.
8. **Edad de los datos del SIE:** archivo de generación descargado el 18-jul-2025 y de consumo en agosto de 2025; no se verificó si el SIE publicó actualizaciones posteriores (por ejemplo, un 2024 de consumo completo).
