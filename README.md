# Proyecto Final · ISLPE05 Inteligencia Artificial (Línea Prof. II) · Grupo 8

**Detección de fraude financiero y bloqueo responsable de cuentas** (inspiración: Ozark).
Técnica: aprendizaje de máquina no supervisado de detección de anomalías (Isolation Forest y
Autoencoder en Python) integrado con un sistema de alertas por niveles con supervisión humana.

Integrantes: Juan Pablo Galeano Restrepo, David Gómez Jiménez y David Sánchez Tabares.
Tarea en el campus: https://campus.ucatolicaluisamigo.edu.co/mod/assign/view.php?id=46277
**Cierre en el campus: lunes 9 de noviembre de 2026, 12:00 m.** (la guía además pedía evidencia
en el repositorio desde el 6 de noviembre: subir cuanto antes).

## Entregables (lo que se sube al campus)
| Entregable de la guía | Archivo en esta carpeta |
|---|---|
| Código fuente funcional y documentado | `codigo/` (comprimir como `codigo_fraude_grupo8.zip`) |
| Resumen ejecutivo de 1 página | `Resumen_Ejecutivo_Fraude_Financiero.docx` |
| Video de máximo 10 minutos | Grabarlo siguiendo `Guion_Video.md` y subir el enlace |
| Apoyo para el video | `Presentacion_Fraude_Financiero.pptx` (9 diapositivas con notas) |
| Análisis ético, legal y social (30 % de la nota) | `Analisis_Etico_Legal.md` |
| Pregunta de debate | Al final del resumen ejecutivo, del guion y de la presentación |
| Resumen de la guía del docente y rúbrica | `00_guia_proyecto_final.md` |

## Cómo ejecutar el código (2 minutos)
```bash
cd codigo
python3 -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py                                        # pipeline completo (≈ 10 s)
python main.py --demo --demo-n 20 --pausa 0.8 --sin-graficos   # simulación en vivo para el video
python -m unittest test_basico -v                     # 4 pruebas
```
En esta carpeta ya existe un entorno listo: `../.venv/bin/python main.py`.

Opciones útiles: `--modelo iforest|autoencoder|ambos`, `--n 100000`, `--fraude 0.002`,
`--presupuesto 0.02` (fracción revisada por analistas), `--csv creditcard.csv` (dataset de Kaggle).

## Qué hace el programa
1. **Datos** (`datos.py`): genera 60.000 transacciones sintéticas reproducibles con 0,5 % de
   fraude en cuatro patrones (card testing, toma de cuenta, tarjeta clonada, fraude sutil) y
   comportamientos legítimos que se parecen al fraude (viajes, compras grandes). No usa datos
   de personas reales.
2. **Modelos** (`modelo.py`): Isolation Forest (scikit-learn) y Autoencoder (`MLPRegressor`
   entrada = salida, capas 8-3-8). Entrenan **sin etiquetas** sobre los primeros 24 días y se
   operan sobre los últimos 6. Puntuación normalizada 0-1.
3. **Evaluación** (`evaluacion.py`): AUC-ROC, AUC-PR, precisión, recall, F1, matriz de
   confusión, recall por patrón y 4 gráficos en `salidas/graficos/`. El umbral se fija por
   "presupuesto de alertas" (1 % de transacciones que el equipo humano puede revisar).
4. **Alertas** (`alertas.py`): niveles BAJO (aprobar), MEDIO (aprobar + OTP), ALTO (retener la
   transacción, avisar al cliente, analista humano con SLA 2 h). Explica cada alerta con las 3
   variables más desviadas y escribe `salidas/alertas.csv` y `salidas/bitacora_decisiones.csv`.
   **El modelo nunca bloquea una cuenta por sí solo.**

### Resultados de la ejecución de referencia (semilla 42, 12.000 transacciones de operación, 50 fraudes)
| Modelo | AUC-ROC | AUC-PR | Precisión | Recall | Fraudes detectados | Falsos positivos | Entrenamiento |
|---|---|---|---|---|---|---|---|
| Isolation Forest | 0,994 | 0,83 | 0,34 | 0,84 | 42 / 50 | 82 | 0,7 s |
| Autoencoder | 0,980 | 0,61 | 0,33 | 0,76 | 38 / 50 | 78 | 1,6 s |

Recall por patrón (Isolation Forest): card testing 100 %, tarjeta clonada 100 %, toma de cuenta
100 %, fraude sutil 11 %. Niveles asignados: 11.650 BAJO, 226 MEDIO, 124 ALTO; 3 propuestas de
bloqueo de cuenta, todas pendientes de analista.

## Estructura
```
inteligenciaArtificial/
├── README.md                              ← este archivo
├── 00_guia_proyecto_final.md              ← resumen de la guía y rúbrica
├── Guion_Video.md                         ← minuto a minuto, reparto, demo, preguntas de sustentación
├── Analisis_Etico_Legal.md                ← dilemas, leyes, responsabilidad, brecha digital
├── Resumen_Ejecutivo_Fraude_Financiero.docx
├── Presentacion_Fraude_Financiero.pptx
├── codigo/
│   ├── main.py            ← punto de entrada (pipeline y --demo)
│   ├── datos.py           ← generador de transacciones / carga CSV
│   ├── modelo.py          ← Isolation Forest y Autoencoder
│   ├── evaluacion.py      ← métricas y gráficos
│   ├── alertas.py         ← sistema de alertas con niveles y bitácora
│   ├── test_basico.py     ← pruebas unitarias
│   └── requirements.txt
├── salidas/               ← se regenera al ejecutar: metricas.csv, alertas.csv, bitácora, graficos/
└── build/                 ← generadores del .docx y del .pptx
```

## Cumplimiento de la rúbrica
- **Demostración y prototipo (30 %)**: código Python funcional, documentado, con pruebas y modo
  demo; técnica coherente con la guía (Isolation Forest / Autoencoder, dataset desbalanceado,
  sistema de alertas).
- **Análisis ético, legal y social (30 %)**: `Analisis_Etico_Legal.md` y sección C del guion:
  principios, leyes colombianas e internacionales, responsabilidad, brecha digital.
- **Calidad audiovisual y tiempo (20 %)**: guion cronometrado por sección con reparto de los 3
  integrantes y presentación de apoyo.
- **Resumen ejecutivo y pregunta de debate (20 %)**: `Resumen_Ejecutivo_Fraude_Financiero.docx`
  (1 página) con la pregunta al final.

## Antes de entregar
1. Ejecutar `python main.py` en el computador donde se grabará y confirmar que corre.
2. Grabar el video con el guion; verificar que dure menos de 10:00.
3. Subir al campus: enlace del video, zip de `codigo/`, resumen ejecutivo (y opcionalmente el pptx).
