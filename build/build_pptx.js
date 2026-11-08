// Presentación de apoyo para el video · Detección de fraude financiero y bloqueo de cuentas
// Uso: NODE_PATH=$PWD/node_modules PPTX_SKILL=<ruta skill pptx> node build_pptx.js ../Presentacion_Fraude_Financiero.pptx
const path = require("path");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(process.env.PPTX_SKILL + "/scripts/apply_theme.js");

const OUT = process.argv[2] || "Presentacion_Fraude_Financiero.pptx";
const GRAF = path.resolve(__dirname, "../salidas/graficos");
const INTEGRANTES = ["Juan Pablo Galeano Restrepo", "David Gómez Jiménez", "David Sánchez Tabares"];

const THEME = {
  name: "Fraude Financiero",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "0B1F3A", lt1: "FFFFFF", dk2: "3A4A5E", lt2: "EEF2F6",
    accent1: "1B8A5A", accent2: "1F3A5F", accent3: "E0A100", accent4: "C62828", accent5: "8A94A3", accent6: "9CC7B4",
    hlink: "1B8A5A", folHlink: "8A94A3",
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625 in
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.author = INTEGRANTES.join(", ");
pres.title = "Detección de fraude financiero y bloqueo responsable de cuentas";
const C = pres.SchemeColor;
const FOOT = "ISLPE05 Inteligencia Artificial · Proyecto Final · Grupo 8";

pres.defineSlideMaster({
  title: "DARK", background: { color: THEME.colors.dk1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 1.5, w: 8.8, h: 1.5, fontSize: 34, bold: true, color: C.background1, valign: "bottom", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.6, y: 3.1, w: 8.8, h: 1.7, fontSize: 16, color: C.background1, valign: "top", margin: 0 }, text: "" } },
    { text: { text: FOOT, options: { x: 0.6, y: 5.15, w: 8.8, h: 0.3, fontSize: 9, color: C.accent5, margin: 0 } } },
  ],
});
pres.defineSlideMaster({
  title: "LIGHT", background: { color: THEME.colors.lt1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.3, w: 9.0, h: 0.7, fontSize: 26, bold: true, color: C.text1, valign: "middle", margin: 0 }, text: "" } },
    { text: { text: FOOT, options: { x: 0.5, y: 5.2, w: 7.5, h: 0.3, fontSize: 9, color: C.accent5, margin: 0 } } },
  ],
  slideNumber: { x: 9.1, y: 5.2, w: 0.5, h: 0.3, fontSize: 9, color: THEME.colors.accent5 },
});

function card(s, x, y, w, h, title, body, o = {}) {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: o.fill || C.background2 }, line: { color: o.fill || C.background2 }, rectRadius: 0.08, objectName: "card " + title });
  s.addText(title, { x: x + 0.15, y: y + 0.1, w: w - 0.3, h: 0.4, fontSize: o.titleSize || 13, bold: true, color: o.titleColor || C.accent2, margin: 0, isTextBox: true, objectName: "card title " + title });
  s.addText(body, { x: x + 0.15, y: y + 0.5, w: w - 0.3, h: h - 0.6, fontSize: o.bodySize || 11, color: o.bodyColor || C.text2, margin: 0, isTextBox: true, valign: "top", objectName: "card body " + title });
}
function stat(s, x, y, w, num, label, color) {
  s.addText(num, { x, y, w, h: 0.75, fontSize: 36, bold: true, color: color || C.accent1, margin: 0, isTextBox: true, objectName: "stat " + label });
  s.addText(label, { x, y: y + 0.75, w, h: 0.5, fontSize: 11, color: C.text2, margin: 0, isTextBox: true, valign: "top", objectName: "stat label " + label });
}
function circle(s, x, y, n, color) {
  s.addShape(pres.ShapeType.ellipse, { x, y, w: 0.4, h: 0.4, fill: { color: color || C.accent1 }, line: { color: color || C.accent1 }, objectName: "circle " + n });
  s.addText(String(n), { x, y, w: 0.4, h: 0.4, fontSize: 13, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "circle n " + n });
}
const bullets = (arr, size = 12) => arr.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < arr.length - 1, fontSize: size, paraSpaceAfter: 4 } }));

// 1. Portada
pres.addSection({ title: "Apertura" });
let s = pres.addSlide({ masterName: "DARK", sectionTitle: "Apertura" });
s.addText("PROYECTO FINAL · GRUPO 8 · INSPIRACIÓN: OZARK", { x: 0.6, y: 0.7, w: 8.8, h: 0.4, fontSize: 12, color: C.accent1, bold: true, charSpacing: 2, margin: 0, isTextBox: true, objectName: "kicker" });
s.addText("Detección de fraude financiero y bloqueo responsable de cuentas", { placeholder: "title" });
s.addText([
  { text: "Aprendizaje de máquina no supervisado (Isolation Forest y Autoencoder) + sistema de alertas con supervisión humana", options: { breakLine: true, fontSize: 15 } },
  { text: " ", options: { breakLine: true, fontSize: 8 } },
  { text: INTEGRANTES.join(" · "), options: { fontSize: 13, color: C.accent6 } },
], { placeholder: "body" });
s.addNotes("Sección A (0:00-1:30). Presentarse y decir el tema en una frase.");

// 2. Contexto y problema
pres.addSection({ title: "Contexto" });
s = pres.addSlide({ masterName: "LIGHT", sectionTitle: "Contexto" });
s.addText("El fraude es raro, cambia de forma y el bloqueo automático castiga inocentes", { placeholder: "title" });
stat(s, 0.5, 1.2, 2.8, "< 1 %", "de las transacciones son fraude: imposible de atender con reglas fijas o revisión manual");
stat(s, 3.6, 1.2, 2.8, "4", "patrones: card testing, toma de cuenta, tarjeta clonada y fraude sutil que imita lo normal", C.accent2);
stat(s, 6.7, 1.2, 2.8, "0", "avisos recibe hoy una persona cuando un algoritmo le congela el salario un viernes en la noche", C.accent4);
card(s, 0.5, 2.9, 4.4, 2.1, "De Ozark a Colombia",
  "Marty Byrde lava dinero en montos pequeños por negocios legítimos para que el banco no lo note. En Colombia el fraude digital (toma de cuentas, clonación, micro-cobros) crece con la banca móvil y la Superfinanciera obliga a monitorear operaciones inusuales (SARLAFT).");
card(s, 5.1, 2.9, 4.4, 2.1, "Nuestra pregunta",
  "¿Cómo detectar fraude en datos con 0,5 % de casos positivos sin convertir cada alerta en un bloqueo injusto? La IA es necesaria por el volumen, la rareza y el cambio constante del fraude; la ética decide qué hacer con la duda.", { fill: THEME.colors.lt2 });
s.addNotes("Juan Pablo. Contexto (0:00-1:30): Ozark, cifras de fraude digital, el problema de los bloqueos sin aviso, por qué requiere IA.");

// 3. Técnica
pres.addSection({ title: "Solución técnica" });
s = pres.addSlide({ masterName: "LIGHT", sectionTitle: "Solución técnica" });
s.addText("Detección de anomalías: aprender lo normal y puntuar lo que se aleja", { placeholder: "title" });
card(s, 0.5, 1.2, 4.4, 2.6, "Isolation Forest (modelo principal)",
  "Construye 300 árboles con cortes aleatorios sobre las 11 variables. Una transacción anómala se aísla en pocos cortes (camino corto); una normal necesita muchos. La puntuación es la profundidad media invertida, normalizada 0-1.\n\nNo necesita etiquetas · 0,7 s de entrenamiento en 48.000 filas · sin GPU.");
card(s, 5.1, 1.2, 4.4, 2.6, "Autoencoder (comparación)",
  "Red neuronal 11 → 8 → 3 → 8 → 11 entrenada para reconstruir su propia entrada (MLPRegressor de scikit-learn). Aprende las transacciones normales; un fraude se reconstruye mal y ese error cuadrático es la anomalía.\n\n60 épocas · 1,6 s · misma interfaz entrenar / puntuar.", { fill: THEME.colors.lt2 });
s.addText([
  { text: "Variables: ", options: { bold: true } },
  { text: "monto, hora, fin de semana, distancia a la ubicación habitual, transacciones en la última hora, monto frente al promedio del cliente, país distinto, dispositivo nuevo, comercio nuevo, intentos fallidos de PIN y canal. Sin nombres ni documentos (minimización de datos)." },
], { x: 0.5, y: 4.0, w: 9.0, h: 0.9, fontSize: 11, color: C.text2, margin: 0, isTextBox: true, valign: "top", objectName: "variables" });
s.addNotes("David Gómez. Explicar las dos técnicas de la unidad de Aprendizaje de Máquinas y por qué no supervisado: con 0,5 % de fraude casi no hay ejemplos positivos.");

// 4. Arquitectura
s = pres.addSlide({ masterName: "LIGHT", sectionTitle: "Solución técnica" });
s.addText("Arquitectura del código: cuatro módulos en Python", { placeholder: "title" });
const mods = [
  ["datos.py", "Genera 60.000 transacciones sintéticas reproducibles (0,5 % fraude, 4 patrones, viajeros y compras grandes legítimas). Carga el CSV de Kaggle."],
  ["modelo.py", "Isolation Forest y Autoencoder con la misma interfaz: entrenar(X) sin etiquetas y puntuar(X) → 0-1."],
  ["evaluacion.py", "AUC-ROC, AUC-PR, precisión, recall, matriz de confusión, recall por patrón y 4 gráficos. Umbral por presupuesto de revisión."],
  ["alertas.py", "Niveles BAJO / MEDIO / ALTO, explicación de cada alerta (3 variables más desviadas) y bitácora auditable en CSV."],
];
mods.forEach(([t, b], i) => {
  const x = 0.5 + (i % 2) * 4.6, y = 1.2 + Math.floor(i / 2) * 1.55;
  circle(s, x, y + 0.08, i + 1);
  s.addText(t, { x: x + 0.55, y, w: 3.9, h: 0.4, fontSize: 14, bold: true, color: C.accent2, margin: 0, isTextBox: true, objectName: "mod " + t });
  s.addText(b, { x: x + 0.55, y: y + 0.42, w: 3.9, h: 1.0, fontSize: 11, color: C.text2, margin: 0, isTextBox: true, valign: "top", objectName: "mod body " + t });
});
s.addShape(pres.ShapeType.roundRect, { x: 0.5, y: 4.3, w: 9.0, h: 0.75, fill: { color: THEME.colors.dk1 }, line: { color: THEME.colors.dk1 }, rectRadius: 0.08, objectName: "flujo" });
s.addText("main.py:  datos  →  entrenar sin etiquetas (días 1-24)  →  puntuar operación (días 25-30)  →  evaluar  →  alertas y bitácora   |   --demo simula transacciones en vivo",
  { x: 0.65, y: 4.3, w: 8.7, h: 0.75, fontSize: 11.5, color: C.background1, margin: 0, isTextBox: true, valign: "middle", objectName: "flujo texto" });
s.addNotes("David Gómez. Mostrar la carpeta codigo/ y pasar a la demo (David Sánchez): python main.py y python main.py --demo.");

// 5. Resultados
s = pres.addSlide({ masterName: "LIGHT", sectionTitle: "Solución técnica" });
s.addText("Resultados: detecta el 84 % del fraude revisando el 1 % de las transacciones", { placeholder: "title" });
s.addChart(pres.ChartType.bar, [
  { name: "Isolation Forest", labels: ["AUC-PR", "Recall", "Precisión"], values: [0.83, 0.84, 0.34] },
  { name: "Autoencoder", labels: ["AUC-PR", "Recall", "Precisión"], values: [0.61, 0.76, 0.33] },
], {
  x: 0.5, y: 1.15, w: 5.2, h: 3.9, barDir: "col", barGrouping: "clustered",
  chartColors: [THEME.colors.accent1, THEME.colors.accent5],
  showTitle: true, title: "Operación: 12.000 transacciones, 50 fraudes (azar: AUC-PR 0,004)", titleFontSize: 11, titleColor: THEME.colors.dk2, titleFontFace: "+mn-lt",
  showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 10, dataLabelColor: THEME.colors.dk2, dataLabelFontFace: "+mn-lt", dataLabelFormatCode: "0.00",
  catAxisLabelColor: THEME.colors.dk2, catAxisLabelFontSize: 11, catAxisLabelFontFace: "+mn-lt",
  valAxisLabelColor: THEME.colors.accent5, valAxisLabelFontSize: 9, valAxisLabelFontFace: "+mn-lt", valAxisMinVal: 0, valAxisMaxVal: 1,
  valGridLine: { color: "DDE3EA", size: 0.5 }, catGridLine: { style: "none" },
  showLegend: true, legendPos: "b", legendFontSize: 10, legendColor: THEME.colors.dk2, legendFontFace: "+mn-lt",
});
stat(s, 6.0, 1.2, 3.5, "42 / 50", "fraudes detectados por Isolation Forest (100 % card testing, clonación y toma de cuenta)");
stat(s, 6.0, 2.5, 3.5, "82", "clientes legítimos con alerta por cada 42 fraudes: el costo ético que hay que gestionar", C.accent4);
stat(s, 6.0, 3.8, 3.5, "11 %", "del fraude sutil se detecta: ningún modelo elimina el fraude, reduce su costo", C.accent3);
s.addNotes("David Sánchez tras la demo. Leer la tabla de la terminal: AUC-PR, recall, falsos positivos. Mostrar 03_precision_recall.png y 04_matriz_confusion.png.");

// 6. Sistema de alertas
s = pres.addSlide({ masterName: "LIGHT", sectionTitle: "Solución técnica" });
s.addText("El modelo decide qué revisar, nunca a quién castigar", { placeholder: "title" });
const niveles = [
  ["BAJO · 11.650", "Aprobar y registrar.\n\nPuntuación por debajo del percentil 97 del entrenamiento.", THEME.colors.accent1],
  ["MEDIO · 226", "Aprobar con verificación OTP o push al cliente. Si confirma, la alerta se cierra.\n\nEj.: un viajero comprando fuera del país.", THEME.colors.accent3],
  ["ALTO · 124", "Retener SOLO esa transacción, avisar al cliente de inmediato y escalar a un analista humano (SLA 2 h).\n\nBloqueo de cuenta únicamente si el analista o el cliente lo confirman (3 propuestas en la corrida).", THEME.colors.accent4],
];
niveles.forEach(([t, b, col], i) => {
  const x = 0.5 + i * 3.05;
  s.addShape(pres.ShapeType.roundRect, { x, y: 1.2, w: 2.9, h: 2.75, fill: { color: THEME.colors.lt2 }, line: { color: THEME.colors.lt2 }, rectRadius: 0.08, objectName: "nivel " + t });
  s.addShape(pres.ShapeType.ellipse, { x: x + 0.15, y: 1.35, w: 0.3, h: 0.3, fill: { color: col }, line: { color: col }, objectName: "punto " + t });
  s.addText(t, { x: x + 0.55, y: 1.3, w: 2.2, h: 0.4, fontSize: 14, bold: true, color: C.text1, margin: 0, isTextBox: true, objectName: "nivel t " + t });
  s.addText(b, { x: x + 0.15, y: 1.8, w: 2.6, h: 2.05, fontSize: 11, color: C.text2, margin: 0, isTextBox: true, valign: "top", objectName: "nivel b " + t });
});
s.addText([
  { text: "Cada alerta se explica: ", options: { bold: true } },
  { text: "“14 transacciones en la última hora; dispositivo nunca visto; 1 intento fallido de PIN”. Todo queda en bitácora (puntuación, nivel, acción, motivos, estado de revisión) para auditoría y derecho a réplica." },
], { x: 0.5, y: 4.15, w: 9.0, h: 0.85, fontSize: 11.5, color: C.text2, margin: 0, isTextBox: true, valign: "top", objectName: "explicacion" });
s.addNotes("David Sánchez con la demo en vivo: mostrar líneas verdes, amarillas y rojas, y abrir salidas/alertas.csv.");

// 7. Ética
pres.addSection({ title: "Análisis ético y legal" });
s = pres.addSlide({ masterName: "LIGHT", sectionTitle: "Análisis ético y legal" });
s.addText("Principios en riesgo si se despliega masivamente, y qué hicimos", { placeholder: "title" });
const etica = [
  ["Autonomía y debido proceso", "Bloqueo sin aviso deja sin dinero a inocentes (2 de cada 3 alertas altas).", "Retener transacciones, no cuentas; aviso inmediato; decisión humana."],
  ["Explicabilidad", "Una puntuación sin motivo no se puede discutir ni apelar.", "3 motivos en lenguaje claro por alerta + bitácora auditable."],
  ["Sesgo y discriminación", "Distancia, país, dispositivo nuevo castigan a viajeros, migrantes y zonas rurales.", "Umbral por capacidad de revisión; evaluación por segmentos; canal alterno."],
  ["Privacidad y habeas data", "Ubicación, hora y dispositivo permiten perfilamiento financiero.", "Finalidad única, 11 variables derivadas, sin identificación, datos sintéticos."],
  ["Responsabilidad", "Nadie firma la decisión del algoritmo.", "La entidad responde ante el cliente; el desarrollador ante la entidad; el analista firma."],
];
s.addTable([
  [{ text: "Principio", options: { bold: true, color: C.background1, fill: { color: THEME.colors.dk1 } } },
   { text: "Riesgo", options: { bold: true, color: C.background1, fill: { color: THEME.colors.dk1 } } },
   { text: "Decisión de diseño en el prototipo", options: { bold: true, color: C.background1, fill: { color: THEME.colors.dk1 } } }],
  ...etica.map(([a, b, c], i) => [
    { text: a, options: { bold: true, color: C.accent2, fill: { color: i % 2 ? THEME.colors.lt1 : THEME.colors.lt2 } } },
    { text: b, options: { color: C.text2, fill: { color: i % 2 ? THEME.colors.lt1 : THEME.colors.lt2 } } },
    { text: c, options: { color: C.text2, fill: { color: i % 2 ? THEME.colors.lt1 : THEME.colors.lt2 } } },
  ]),
], { x: 0.5, y: 1.15, w: 9.0, colW: [2.2, 3.2, 3.6], fontSize: 10.5, border: { type: "solid", color: "DDE3EA", pt: 0.5 }, margin: 0.06, valign: "middle", rowH: [0.35, 0.72, 0.6, 0.72, 0.72, 0.72], objectName: "tabla etica" });
s.addNotes("David Gómez (5:00-6:40). Dilema: 2 de cada 3 alertas altas son clientes inocentes. Recorrer la tabla principio por principio diciendo qué hace el prototipo.");

// 8. Marco legal
s = pres.addSlide({ masterName: "LIGHT", sectionTitle: "Análisis ético y legal" });
s.addText("Marco normativo y asignación de responsabilidad", { placeholder: "title" });
card(s, 0.5, 1.15, 4.4, 3.0, "Colombia",
  "• Constitución art. 15: intimidad y habeas data\n• Ley 1266 de 2008 y Ley 2157 de 2021: habeas data financiero\n• Ley 1581 de 2012 y Decreto 1377 de 2013: datos personales (finalidad, transparencia, seguridad; vigila la SIC)\n• Ley 1328 de 2009: consumidor financiero y Defensor del Consumidor Financiero\n• Ley 1273 de 2009: hurto por medios informáticos, transferencia no consentida de activos\n• Superfinanciera: C.E. 007 y 008 de 2018 (ciberseguridad) y SARLAFT (reporte de operaciones sospechosas a la UIAF)\n• CONPES 3975 de 2019 y 4144 de 2025: política de IA", { bodySize: 10.5 });
card(s, 5.1, 1.15, 4.4, 3.0, "Internacional",
  "• GDPR art. 22: derecho a no ser objeto de decisiones únicamente automatizadas; intervención humana y derecho a impugnar. Arts. 13-15: información sobre la lógica aplicada\n• Ley de IA de la UE (2024/1689): la detección de fraude financiero queda fuera de “alto riesgo”, pero sigue la obligación de transparencia\n• Recomendación UNESCO 2021: proporcionalidad, no discriminación, privacidad, supervisión humana, explicabilidad, rendición de cuentas\n• Principios de IA de la OCDE (2019)", { fill: THEME.colors.lt2, bodySize: 10.5 });
s.addShape(pres.ShapeType.roundRect, { x: 0.5, y: 4.3, w: 9.0, h: 0.75, fill: { color: THEME.colors.dk1 }, line: { color: THEME.colors.dk1 }, rectRadius: 0.08, objectName: "resp" });
s.addText([
  { text: "¿Quién responde si falla?  ", options: { bold: true, color: C.accent6 } },
  { text: "La entidad financiera ante el cliente (Ley 1328, SFC) · el desarrollador ante la entidad (documentar límites y validación) · el analista firma la decisión final · brecha digital: sin canal alterno al OTP, la verificación es un bloqueo de facto.", options: { color: C.background1 } },
], { x: 0.65, y: 4.3, w: 8.7, h: 0.75, fontSize: 10.5, margin: 0, isTextBox: true, valign: "middle", objectName: "resp texto" });
s.addNotes("David Sánchez (6:40-7:40) leyes; Juan Pablo (7:40-8:30) responsabilidad y brecha digital.");

// 9. Conclusiones y pregunta
pres.addSection({ title: "Cierre" });
s = pres.addSlide({ masterName: "DARK", sectionTitle: "Cierre" });
s.addText("CONCLUSIONES", { x: 0.6, y: 0.5, w: 8.8, h: 0.4, fontSize: 12, color: C.accent1, bold: true, charSpacing: 2, margin: 0, isTextBox: true, objectName: "kicker 2" });
s.addText(bullets([
  "En fraude la métrica honesta no es la exactitud: es el AUC-PR y, sobre todo, los falsos positivos.",
  "Un modelo no supervisado funciona con 0,5 % de fraude, pero deja pasar el fraude que imita lo normal (11 %).",
  "Lo más difícil no fue el modelo: fue diseñar qué pasa después de la alerta. Supervisión humana, explicación y derecho a réplica son requisitos legales, no adornos.",
], 15), { x: 0.6, y: 0.95, w: 8.8, h: 2.0, color: C.background1, margin: 0, isTextBox: true, valign: "top", objectName: "conclusiones" });
s.addShape(pres.ShapeType.roundRect, { x: 0.6, y: 3.15, w: 8.8, h: 1.75, fill: { color: THEME.colors.accent2 }, line: { color: THEME.colors.accent2 }, rectRadius: 0.1, objectName: "pregunta caja" });
s.addText([
  { text: "PREGUNTA PARA EL AULA", options: { bold: true, fontSize: 11, color: C.accent6, breakLine: true, charSpacing: 2 } },
  { text: "Si el modelo detecta el 84 % de los fraudes pero por cada 42 fraudes reales señala a 82 clientes inocentes, ¿tiene derecho un banco a retener tu dinero “por tu seguridad” sin que un humano haya revisado el caso? ¿Preferirían un banco que bloquea de más o uno que bloquea de menos?", options: { fontSize: 15, color: C.background1, italic: true } },
], { x: 0.85, y: 3.25, w: 8.3, h: 1.55, margin: 0, isTextBox: true, valign: "middle", objectName: "pregunta" });
s.addNotes("Sección D (8:30-10:00). Conclusiones (David Gómez y David Sánchez) y pregunta abierta (Juan Pablo). Terminar antes de 10:00.");

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("Guardado", OUT);
})();
