# Guion del video (máximo 10:00) · Detección de fraude financiero y bloqueo de cuentas

Reparto para los 3 integrantes. Cada uno debe aparecer en cámara y
hablar con fluidez de su parte: la rúbrica califica integración de todos los miembros (20 %)
y manejo estricto del tiempo. Grabar con pantalla compartida y cámara visible (Meet/Zoom/OBS).

| Sección | Tiempo | Quién | Duración |
|---|---|---|---|
| A. Contexto y problema social | 0:00-1:30 | Juan Pablo Galeano | 1:30 |
| B. Solución técnica y demo en vivo | 1:30-5:00 | David Gómez (arquitectura) + David Sánchez (demo) | 3:30 |
| C. Análisis ético, legal y social | 5:00-8:30 | David Gómez (dilema y principios) + David Sánchez (marco legal) + Juan Pablo (responsabilidad y brecha digital) | 3:30 |
| D. Conclusiones y pregunta abierta | 8:30-10:00 | Todos (pregunta final: Juan Pablo) | 1:30 |

Antes de grabar: abrir una terminal grande (fuente 18+), ejecutar `python main.py` una vez
para que las salidas existan, tener abiertas las imágenes de `salidas/graficos/` y la
presentación `Presentacion_Fraude_Financiero.pptx`.

---

## A. Contexto y problema social (0:00-1:30) · Juan Pablo Galeano
**[Diapositiva 1-2]**

"En Ozark, Marty Byrde lava millones moviéndolos en montos pequeños por negocios legítimos
para que ningún sistema del banco se dé cuenta. Eso que en la serie es ficción, en Colombia
es un problema diario: la Superintendencia Financiera recibe cientos de miles de quejas al año
por fraude en canales digitales, y el fraude con tarjetas y toma de cuentas crece con la
banca móvil."

"Los bancos responden con sistemas automáticos que bloquean cuentas cuando algo se ve raro.
El problema es el otro lado: personas a las que les bloquean el salario, el arriendo o la
medicina un viernes en la noche, sin aviso, sin saber por qué, porque un algoritmo las
confundió con un delincuente."

"Esto requiere IA por tres razones: hay millones de transacciones por día, el fraude es
menos del 1 % y cambia de forma constantemente, así que no se pueden escribir reglas fijas.
Nuestra pregunta fue: ¿cómo detectar fraude en datos tan desbalanceados **sin** convertir
cada alerta en un bloqueo injusto?"

## B. Solución técnica (1:30-5:00)

### B1. Arquitectura (1:30-2:45) · David Gómez Jiménez
**[Diapositiva 3-4]**

"Usamos aprendizaje de máquina **no supervisado**: detección de anomalías. No le enseñamos
al modelo qué es fraude, porque casi no hay ejemplos; le enseñamos qué es normal y marcamos
lo que se aleja."

"El código tiene cuatro módulos en Python:
1. `datos.py` genera 60.000 transacciones sintéticas con 0,5 % de fraude, con cuatro patrones
   reales: card testing, toma de cuenta, tarjeta clonada y un fraude sutil que imita lo normal.
   También carga el dataset público de Kaggle.
2. `modelo.py` implementa dos detectores con la misma interfaz: **Isolation Forest**, que aísla
   puntos con cortes aleatorios y los anómalos se aíslan en pocos cortes; y un **Autoencoder**,
   una red neuronal que aprende a reconstruir transacciones normales y falla al reconstruir
   fraudes. Ambos devuelven una puntuación entre 0 y 1.
3. `evaluacion.py` mide con las métricas correctas para clases raras: AUC-PR, precisión,
   recall y, sobre todo, falsos positivos.
4. `alertas.py` convierte la puntuación en tres niveles: BAJO aprueba; MEDIO aprueba pero
   pide OTP; ALTO retiene **solo esa transacción**, avisa al cliente y la pasa a un analista
   humano. El modelo nunca bloquea una cuenta."

### B2. Demostración en vivo (2:45-5:00) · David Sánchez Tabares
**[Terminal]** Ejecutar:

```bash
cd codigo
python main.py
```

Mientras corre, narrar:
- "Se generan 60.000 transacciones; solo 300 son fraude. Entrenamos con 48.000 del pasado y
  operamos sobre 12.000 recientes."
- "Isolation Forest entrena en menos de un segundo; el autoencoder en dos."
- Señalar la tabla: "AUC-PR de 0,83 contra 0,004 del azar. Con un presupuesto de revisión del
  1 % detectamos el 84 % de los fraudes: 42 de 50. Pero miren la columna de falsos positivos:
  82 clientes legítimos recibirían una alerta. Ese número es el centro del debate ético."
- Señalar recall por tipo: "Card testing, clonación y toma de cuenta: 100 %. Fraude sutil: 11 %.
  El modelo no es mágico."
- Mostrar `salidas/graficos/03_precision_recall.png` y `04_matriz_confusion.png` (10 s cada uno).
- Señalar la tabla nivel vs. realidad: "11.650 aprobadas, 226 con OTP, 124 retenidas para un
  humano. Solo 3 propuestas de bloqueo de cuenta, todas pendientes de analista."

Luego ejecutar la simulación en vivo:

```bash
python main.py --demo --demo-n 20 --pausa 0.8 --sin-graficos
```

- "Cada línea es una transacción llegando. Verde: aprobada. Amarilla: el cliente recibe un OTP,
  por ejemplo este viajero comprando fuera del país. Roja: retenida; miren el motivo:
  '14 transacciones en la última hora, dispositivo nunca visto'. Esa explicación es lo que
  recibe el analista y el cliente."
- Abrir `salidas/alertas.csv` 5 segundos: "Todo queda en bitácora: puntuación, nivel, acción,
  motivos y estado de revisión."

## C. Análisis ético, legal y social (5:00-8:30)
**[Diapositivas 5-7]** Apoyarse en `Analisis_Etico_Legal.md`.

1. **El dilema (5:00-5:40) · David Gómez:** "Dos de cada tres alertas altas son clientes inocentes. Si la
   alerta fuera un bloqueo automático, el sistema castigaría más inocentes que delincuentes.
   Por eso la decisión central no está en el modelo sino en qué hace el sistema con la duda."
2. **Principios en riesgo (5:40-6:40) · David Gómez:** autonomía y debido proceso (bloqueo sin aviso),
   explicabilidad (puntuación sin motivo no se puede apelar), sesgo (distancia, país,
   dispositivo nuevo castigan a migrantes, viajeros, zonas rurales), privacidad y perfilamiento
   financiero (datos de ubicación y comportamiento solo para prevenir fraude), proporcionalidad.
   Decir en cada uno qué hizo el prototipo: niveles, motivos explicables, bitácora, umbral por
   capacidad de revisión.
3. **Marco legal (6:40-7:40) · David Sánchez:** Constitución art. 15 (habeas data); Ley 1266 de 2008 y Ley 2157
   de 2021 (habeas data financiero); Ley 1581 de 2012 (datos personales, principios de finalidad
   y transparencia, vigilancia de la SIC); Ley 1328 de 2009 (consumidor financiero, Defensor);
   Ley 1273 de 2009 (delitos informáticos); Superfinanciera: Circulares 007 y 008 de 2018 de
   ciberseguridad y SARLAFT (reporte de operaciones sospechosas a la UIAF, el vínculo con
   Ozark). Internacional: GDPR art. 22 (derecho a no ser objeto de decisiones solo automatizadas
   y a intervención humana), Ley de IA de la UE (detección de fraude exceptuada de "alto riesgo",
   pero con obligaciones de transparencia), Recomendación UNESCO 2021 (supervisión humana,
   explicabilidad, rendición de cuentas), CONPES 4144 de 2025.
4. **Responsabilidad y brecha digital (7:40-8:30) · Juan Pablo:** responde la entidad
   financiera ante el cliente (relación contractual y regulatoria); el desarrollador responde
   ante la entidad por documentar límites y validación; el analista firma la decisión final.
   Brecha digital: la verificación por OTP supone smartphone y datos; sin canal alterno
   (llamada, oficina, corresponsal) la verificación es un bloqueo de facto para mayores y
   zonas rurales.

## D. Conclusiones y pregunta abierta (8:30-10:00)
**[Diapositivas 8-9]**

- David Gómez: "Aprendimos que en fraude la métrica importante no es la exactitud sino el
  AUC-PR y los falsos positivos; que un modelo no supervisado funciona bien con 0,5 % de fraude
  pero deja pasar el fraude que imita lo normal; y que la parte más difícil no fue el modelo,
  fue diseñar qué pasa después de la alerta."
- David Sánchez: "Lección: la IA debe decidir **qué revisar**, no **a quién castigar**. Supervisión
  humana, explicación y derecho a réplica no son adornos, son requisitos legales."
- Juan Pablo (cierre, mirando a cámara): **Pregunta para el aula:**
  > "Si el modelo detecta el 84 % de los fraudes pero por cada 42 fraudes reales señala a 82
  > clientes inocentes, ¿tiene derecho un banco a retener tu dinero 'por tu seguridad' sin que
  > un humano haya revisado el caso? ¿Preferirían un banco que bloquea de más o uno que bloquea
  > de menos?"

Terminar antes de 10:00. Dejar 5 segundos de pantalla final con nombres del equipo.

---

## Lista de verificación antes de subir
- [ ] El video dura menos de 10:00 y todos aparecen en cámara.
- [ ] Se ve la ejecución real de `python main.py` y de `--demo` en pantalla.
- [ ] Se nombran las leyes colombianas y al menos una internacional (GDPR / UNESCO).
- [ ] Se dice explícitamente quién responde si falla y se menciona la brecha digital.
- [ ] Se formula la pregunta abierta al final.
- [ ] Subir al campus: enlace del video, `codigo/` (zip), `Resumen_Ejecutivo_Fraude_Financiero.docx`.

## Posibles preguntas del docente (sustentación aleatoria)
- ¿Por qué no usar un clasificador supervisado? Porque con 0,5 % de fraude casi no hay
  ejemplos positivos y el fraude cambia; el no supervisado aprende lo normal. Si hubiera
  etiquetas confirmadas, se combinarían (semi-supervisado).
- ¿Cómo funciona Isolation Forest? Construye árboles con cortes aleatorios; una anomalía se
  aísla con pocos cortes (camino corto). El score es la profundidad media invertida.
- ¿Y el autoencoder? Red que comprime (11 → 8 → 3) y reconstruye (3 → 8 → 11); el error de
  reconstrucción es la anomalía. Se entrenó con `MLPRegressor` de scikit-learn.
- ¿Por qué el umbral del 1 %? Es el presupuesto de alertas que un equipo de analistas puede
  revisar; convierte una decisión estadística en una decisión operativa y ética explícita.
- ¿Qué es el costo de máquina? Isolation Forest: ~0,7 s en 48.000 filas, lineal en el número de
  árboles; el autoencoder ~1,6 s con 60 épocas. Ambos corren en un portátil sin GPU.
- ¿Qué pasa con el fraude sutil? Solo 11 % de recall: hay que combinar con reglas de negocio,
  grafos de relaciones entre cuentas y retroalimentación de casos confirmados.
