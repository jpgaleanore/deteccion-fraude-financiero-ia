# -*- coding: utf-8 -*-
"""Genera el Resumen Ejecutivo (1 página) en Word.
Uso: ../.venv/bin/python build_resumen.py ../Resumen_Ejecutivo_Fraude_Financiero.docx
"""
import sys

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

OUT = sys.argv[1] if len(sys.argv) > 1 else "Resumen_Ejecutivo_Fraude_Financiero.docx"
AZUL = RGBColor(0x0B, 0x1F, 0x3A)
VERDE = RGBColor(0x1B, 0x8A, 0x5A)
GRIS = RGBColor(0x55, 0x55, 0x55)

INTEGRANTES = "Juan Pablo Galeano Restrepo · David Gómez Jiménez · David Sánchez Tabares"
CURSO = "ISLPE05 Inteligencia Artificial (Línea Prof. II) G1 · Universidad Católica Luis Amigó · Proyecto Final · Grupo 8 · noviembre de 2026"


def shade(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


doc = Document()
sec = doc.sections[0]
sec.page_height, sec.page_width = Cm(27.94), Cm(21.59)  # carta
for side in ("left_margin", "right_margin"):
    setattr(sec, side, Cm(1.7))
sec.top_margin, sec.bottom_margin = Cm(1.4), Cm(1.2)

normal = doc.styles["Normal"]
normal.font.name = "Calibri"
normal.font.size = Pt(9.5)
normal.paragraph_format.space_after = Pt(2)
normal.paragraph_format.line_spacing = 1.0


def p(text, bold=False, size=None, color=None, align=None, after=2, italic=False):
    par = doc.add_paragraph()
    r = par.add_run(text)
    r.bold, r.italic = bold, italic
    if size:
        r.font.size = Pt(size)
    if color is not None:
        r.font.color.rgb = color
    if align:
        par.alignment = align
    par.paragraph_format.space_after = Pt(after)
    return par


def h(text):
    par = p(text, bold=True, size=11, color=AZUL, after=1)
    par.paragraph_format.space_before = Pt(4)
    par.paragraph_format.keep_with_next = True
    return par


def rich(parts, after=2):
    par = doc.add_paragraph()
    for text, bold in parts:
        r = par.add_run(text)
        r.bold = bold
    par.paragraph_format.space_after = Pt(after)
    return par


# ---- Encabezado --------------------------------------------------------------------------------
p("RESUMEN EJECUTIVO", bold=True, size=9, color=VERDE, after=0)
p("Detección de fraude financiero y bloqueo responsable de cuentas", bold=True, size=16, color=AZUL, after=0)
p("Aprendizaje de máquina no supervisado (Isolation Forest y Autoencoder) integrado con un sistema de alertas con supervisión humana · Inspiración: Ozark",
  italic=True, size=9.5, color=GRIS, after=1)
p(f"{CURSO}\n{INTEGRANTES}\nCódigo fuente: https://github.com/jpgaleanore/deteccion-fraude-financiero-ia", size=8.5, color=GRIS, after=4)

# ---- 1. Problema -------------------------------------------------------------------------------
h("1. Problema")
p("El fraude en canales digitales (toma de cuentas, tarjetas clonadas, micro-cobros de prueba) representa menos del 1 % de las "
  "transacciones, cambia de forma constantemente y ocurre en volúmenes de millones de operaciones por día: no se puede "
  "atender con reglas fijas ni con revisión manual. La respuesta habitual de las entidades, bloquear automáticamente la cuenta "
  "ante cualquier comportamiento inusual, traslada el costo del error a personas legítimas que quedan sin acceso a su dinero, "
  "sin aviso y sin explicación. El reto es doble: detectar el fraude en datos altamente desbalanceados y decidir de forma "
  "proporcional y auditable qué hacer con cada alerta.")

# ---- 2. Técnica --------------------------------------------------------------------------------
h("2. Técnica de IA")
rich([("Detección de anomalías no supervisada. ", True),
      ("El modelo no aprende qué es fraude (casi no hay ejemplos), aprende qué es normal y puntúa cuánto se aleja cada "
       "transacción. Se comparan dos técnicas: ", False),
      ("Isolation Forest", True),
      (" (árboles con cortes aleatorios: las anomalías se aíslan en pocos cortes) y un ", False),
      ("Autoencoder", True),
      (" (red neuronal 11-8-3-8-11 que reconstruye transacciones normales; el error de reconstrucción es la anomalía). "
       "El umbral de alerta se fija por presupuesto de revisión (el 1 % más anómalo), lo que hace explícito el costo humano.", False)])

# ---- 3. Arquitectura ---------------------------------------------------------------------------
h("3. Arquitectura del código (Python 3, scikit-learn, pandas, matplotlib)")
rich([("datos.py", True), (" genera 60.000 transacciones sintéticas reproducibles con 0,5 % de fraude en cuatro patrones "
      "(card testing, toma de cuenta, tarjeta clonada, fraude sutil) y comportamientos legítimos parecidos al fraude; también carga el dataset público de Kaggle. ", False),
      ("modelo.py", True), (" implementa los dos detectores con la misma interfaz (entrenar / puntuar 0-1). ", False),
      ("evaluacion.py", True), (" calcula AUC-ROC, AUC-PR, precisión, recall, matriz de confusión, recall por patrón y gráficos. ", False),
      ("alertas.py", True), (" convierte la puntuación en tres niveles: BAJO aprueba; MEDIO aprueba con verificación OTP; "
      "ALTO retiene solo la transacción, avisa al cliente y la escala a un analista humano (SLA 2 h). Cada alerta se explica con las "
      "tres variables más desviadas y queda en una bitácora auditable. ", False),
      ("main.py", True), (" ejecuta el pipeline completo y un modo --demo que simula transacciones en vivo. El modelo nunca bloquea una cuenta por sí solo.", False)])

# ---- 4. Resultados -----------------------------------------------------------------------------
h("4. Resultados (12.000 transacciones de operación, 50 fraudes reales, presupuesto de revisión 1 %)")
filas = [
    ("Isolation Forest", "0,994", "0,83", "0,34", "0,84", "42 / 50", "82", "0,7 s"),
    ("Autoencoder", "0,980", "0,61", "0,33", "0,76", "38 / 50", "78", "1,6 s"),
]
enc = ["Modelo", "AUC-ROC", "AUC-PR", "Precisión", "Recall", "Fraudes detectados", "Falsos positivos", "Entrenamiento"]
t = doc.add_table(rows=1 + len(filas), cols=len(enc))
t.style = "Table Grid"
t.alignment = WD_TABLE_ALIGNMENT.CENTER
for i, e in enumerate(enc):
    c = t.rows[0].cells[i]
    c.text = ""
    r = c.paragraphs[0].add_run(e)
    r.bold, r.font.size = True, Pt(8.5)
    shade(c, "DCE6F1")
for ri, fila in enumerate(filas, start=1):
    for ci, v in enumerate(fila):
        c = t.rows[ri].cells[ci]
        c.text = ""
        r = c.paragraphs[0].add_run(v)
        r.font.size = Pt(8.5)
        r.bold = ci == 0
for row in t.rows:
    for c in row.cells:
        c.paragraphs[0].paragraph_format.space_after = Pt(0)
p("El azar daría AUC-PR ≈ 0,004. Isolation Forest detecta el 100 % del card testing, la clonación y la toma de cuenta, pero solo el 11 % del "
  "fraude sutil que imita el comportamiento normal. Lectura clave: por cada 42 fraudes detectados, 82 clientes legítimos recibirían una alerta; "
  "en el sistema de niveles esas alertas se traducen en 226 verificaciones OTP y 124 revisiones humanas, con solo 3 propuestas de bloqueo de cuenta, todas sujetas a un analista.",
  size=9, after=2)
doc.paragraphs[-1].paragraph_format.space_before = Pt(2)

# ---- 5. Conclusiones éticas --------------------------------------------------------------------
h("5. Conclusiones éticas y legales")
for texto in [
    ("Autonomía y debido proceso. ", "Un bloqueo automático sin aviso castiga más inocentes que delincuentes (2 de cada 3 alertas altas). El sistema retiene transacciones, no cuentas, "
     "avisa de inmediato y exige decisión humana, en línea con el art. 22 del GDPR y la Recomendación UNESCO 2021 (supervisión humana, derecho a réplica)."),
    ("Explicabilidad y rendición de cuentas. ", "Cada alerta lleva motivos en lenguaje claro y queda en bitácora; sin eso no hay apelación posible ni cumplimiento de los principios de transparencia de la Ley 1581 de 2012."),
    ("Sesgo y brecha digital. ", "Variables como distancia, país o dispositivo nuevo se parecen al fraude en viajeros, migrantes y zonas rurales; la verificación por OTP supone smartphone. "
     "Se requiere evaluación por segmentos y canales alternos (llamada, oficina)."),
    ("Privacidad y habeas data. ", "Datos financieros y de comportamiento solo para prevenir fraude (finalidad única), con minimización (11 variables derivadas, sin identificación): "
     "Constitución art. 15, Ley 1266 de 2008 / Ley 2157 de 2021, Ley 1581 de 2012, Ley 1328 de 2009 (Defensor del Consumidor Financiero), Circulares 007 y 008 de 2018 y SARLAFT de la Superfinanciera."),
    ("Responsabilidad. ", "Responde la entidad financiera ante el cliente; el desarrollador ante la entidad por documentar límites y validación; el analista firma la decisión final. "
     "La Ley de IA de la UE exceptúa la detección de fraude de la categoría de alto riesgo, pero no de la transparencia."),
]:
    par = doc.add_paragraph(style="List Bullet")
    r = par.add_run(texto[0]); r.bold = True
    par.add_run(texto[1])
    par.paragraph_format.space_after = Pt(1)
    for r in par.runs:
        r.font.size = Pt(9)

# ---- Pregunta ----------------------------------------------------------------------------------
h("Pregunta de debate")
par = p("Si un modelo detecta el 84 % de los fraudes pero por cada 42 fraudes reales señala a 82 clientes inocentes, ¿tiene derecho un banco a retener tu dinero "
        "“por tu seguridad” sin que un humano haya revisado el caso? ¿Preferirías un banco que bloquea de más o uno que bloquea de menos?",
        italic=True, size=10, color=AZUL, after=0)

doc.save(OUT)
print("Guardado", OUT)
