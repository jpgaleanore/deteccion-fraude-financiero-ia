# Análisis ético, legal y social · Detección de fraude y bloqueo de cuentas

Material de apoyo para la sección C del video (5:00-8:30) y para la sustentación.
Vale el 30 % de la nota: la rúbrica pide "identificación rigurosa de dilemas, marcos
regulatorios aplicables y asignación de responsabilidad".

## 1. El dilema en una frase
Un modelo que detecta el 84 % de los fraudes revisando solo el 1 % de las transacciones
también marca a **82 clientes legítimos por cada 42 fraudes reales** (resultado de nuestra
ejecución). Si cada alerta se convirtiera en un bloqueo automático, dos de cada tres
personas bloqueadas serían inocentes. El problema no es solo técnico: es decidir **qué
hace el sistema con la duda**.

## 2. Principios en riesgo (y cómo el prototipo los atiende)

| Principio | Riesgo si se despliega masivamente | Decisión de diseño en el prototipo |
|---|---|---|
| **Autonomía y debido proceso** | Bloquear la cuenta sin aviso deja a la persona sin acceso a su dinero (arriendo, salud, comida) y sin saber por qué. | El modelo nunca bloquea. Nivel ALTO = retener solo la transacción, avisar al cliente de inmediato y escalar a un analista humano con SLA de 2 h. El bloqueo de cuenta requiere confirmación humana o del propio cliente. |
| **Explicabilidad / transparencia** | Isolation Forest y autoencoders son modelos "caja negra": una puntuación sin motivo no se puede discutir ni apelar. | Cada alerta lleva los 3 motivos más desviados en lenguaje claro ("transacción fuera del país", "14 operaciones en la última hora") y queda en una bitácora auditable. |
| **No discriminación / sesgo** | Variables como distancia, país, dispositivo nuevo o canal pueden castigar a migrantes, viajeros, personas que comparten celular o viven en zonas rurales. "Anómalo" no es igual a "fraudulento". | Umbrales por presupuesto de revisión (no por "sospecha"), fallback de verificación por llamada o en oficina, medición del recall y de los falsos positivos por segmento antes de operar. |
| **Privacidad y habeas data** | El sistema procesa datos financieros y de comportamiento (ubicación, hora, dispositivo). Usarlos para otro fin (marketing, scoring) sería perfilamiento financiero. | Minimización: 11 variables derivadas, sin nombres ni documentos. Finalidad única (prevención de fraude). Datos sintéticos en el prototipo. |
| **Seguridad y proporcionalidad** | Un sistema demasiado sensible "protege" congelando; uno demasiado laxo deja pasar fraudes (nuestro "fraude sutil" solo se detecta en 11 %). | Tres niveles proporcionales (aprobar / OTP / retener + humano) y revisión periódica de umbrales con casos confirmados. |
| **Responsabilidad y rendición de cuentas** | Nadie "firma" la decisión de un algoritmo. | Bitácora con fecha, puntuación, nivel, acción, motivos y estado de revisión; el analista deja trazabilidad de la decisión final. |

## 3. Marco normativo aplicable

### Colombia
- **Constitución Política, art. 15**: derecho a la intimidad y al habeas data (conocer, actualizar y rectificar la información recogida sobre uno).
- **Ley 1266 de 2008** (habeas data financiero), modificada por la **Ley 2157 de 2021**: trata los datos financieros y crediticios; exige veracidad, finalidad, circulación restringida y derecho de la persona a reclamar.
- **Ley 1581 de 2012 y Decreto 1377 de 2013** (protección de datos personales): principios de finalidad, libertad, veracidad, transparencia, acceso y circulación restringida, seguridad y confidencialidad. La Superintendencia de Industria y Comercio (SIC) sanciona su incumplimiento.
- **Ley 1328 de 2009** (régimen de protección al consumidor financiero): derecho a recibir información clara, a presentar quejas, y figura del Defensor del Consumidor Financiero; es la vía de apelación cuando una entidad retiene o bloquea.
- **Ley 1273 de 2009** (delitos informáticos): tipifica el hurto por medios informáticos (art. 269I) y la transferencia no consentida de activos (art. 269J), que son justamente los fraudes que el sistema busca detectar.
- **Superintendencia Financiera de Colombia (SFC)**: Circular Básica Jurídica (C.E. 029 de 2014) con requisitos mínimos de seguridad y calidad en canales; **Circulares Externas 007 y 008 de 2018** sobre gestión del riesgo de ciberseguridad y seguridad de la información; **SARLAFT** (C.E. 027 de 2020) que obliga a monitorear operaciones inusuales y reportar operaciones sospechosas (ROS) a la UIAF. Conexión directa con Ozark: el lavado de activos se detecta como anomalías de comportamiento transaccional.
- **CONPES 3975 de 2019 y CONPES 4144 de 2025** (política nacional de IA): ética, transparencia, explicabilidad y supervisión humana como lineamientos del Estado colombiano.

### Internacional
- **GDPR (Reglamento UE 2016/679), art. 22**: la persona tiene derecho a no ser objeto de decisiones basadas únicamente en tratamiento automatizado que produzcan efectos jurídicos o le afecten significativamente; exige intervención humana, derecho a expresar su punto de vista y a impugnar. Arts. 13-15: derecho a información significativa sobre la lógica aplicada.
- **Ley de IA de la Unión Europea (Reglamento 2024/1689)**: la evaluación de solvencia de personas es de alto riesgo (Anexo III), pero los sistemas usados **para detectar fraude financiero quedan expresamente exceptuados** de esa categoría. Aun así aplican obligaciones de transparencia y los principios generales de supervisión humana.
- **Recomendación de la UNESCO sobre la ética de la IA (2021)**: proporcionalidad e inocuidad, seguridad, equidad y no discriminación, privacidad, supervisión y decisión humanas, transparencia y explicabilidad, responsabilidad y rendición de cuentas.
- **Principios de IA de la OCDE (2019)**: crecimiento inclusivo, valores centrados en el ser humano, transparencia, robustez y rendición de cuentas.

## 4. ¿Quién responde si falla?
- **La entidad financiera que implementa** es la responsable frente al cliente: es quien tiene la relación contractual y la obligación regulatoria (Ley 1328, SFC). Un bloqueo injustificado es una falla en la prestación del servicio, y puede reclamarse ante el Defensor del Consumidor Financiero y la SFC.
- **El desarrollador / proveedor del modelo** responde contractualmente ante la entidad: debe documentar el modelo, sus límites (p. ej. el recall de 11 % en fraude sutil), su validación y entregar mecanismos de explicabilidad y monitoreo. La entidad no puede "delegar la culpa" en el algoritmo.
- **El analista humano** que confirma un bloqueo asume la decisión final; por eso la bitácora registra quién decidió y con qué evidencia.
- **El cliente** conserva la carga de reportar fraude, pero no puede ser penalizado por el error del modelo (p. ej. intereses o sanciones durante una retención injustificada).

## 5. Brecha digital y equidad
- La verificación por OTP/push supone un celular con datos. Personas mayores, zonas rurales o clientes sin smartphone necesitan un **canal alterno** (llamada, oficina, corresponsal bancario); de lo contrario la "verificación" se convierte en un bloqueo de facto.
- Comportamientos legítimos de poblaciones específicas (migrantes que envían remesas, trabajadores informales con ingresos irregulares, viajeros) se parecen estadísticamente al fraude. El modelo debe evaluarse por segmentos y los umbrales ajustarse, o se castiga sistemáticamente a los mismos grupos.
- El fraude también es un problema de equidad: quienes más pierden con un fraude no detectado son quienes menos ahorro tienen. Por eso la respuesta no es "no usar IA", sino usarla con proporcionalidad y supervisión.

## 6. Lo que el prototipo NO resuelve (para decirlo con honestidad)
- Datos sintéticos: la validación real exige datos históricos con casos confirmados y una evaluación de sesgo por segmento.
- El autoencoder se entrenó con una red pequeña (scikit-learn); en producción se usaría PyTorch/TensorFlow con más datos.
- El "fraude sutil" casi no se detecta (11 %): ningún sistema elimina el fraude; reduce su costo y velocidad.
- La explicabilidad por z-scores es una aproximación; en producción se usarían técnicas como SHAP.

## 7. Pregunta de debate
> Si un modelo detecta el 84 % de los fraudes pero por cada 42 fraudes reales marca a 82 clientes inocentes,
> ¿tiene derecho un banco a retener tu dinero "por tu seguridad" sin que un humano haya revisado el caso?
> ¿Y preferirías tú un banco que te bloquea de más o uno que te bloquea de menos?
