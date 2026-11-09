# Detección de fraude financiero con detección de anomalías

Prototipo en Python que identifica transacciones bancarias sospechosas en un conjunto de datos altamente desbalanceado (0,5 % de fraude) y las convierte en alertas con supervisión humana.

## Qué hace

- Genera transacciones sintéticas con patrones de fraude (card testing, toma de cuenta, tarjeta clonada, fraude sutil) o carga un CSV propio / el dataset público de Kaggle.
- Entrena dos detectores **no supervisados** (aprenden lo normal, sin etiquetas): Isolation Forest y un Autoencoder.
- Puntúa cada transacción de 0 a 1 y evalúa con métricas para clases raras (AUC-PR, precisión, recall, falsos positivos).
- Clasifica cada transacción en tres niveles: **BAJO** aprueba, **MEDIO** pide verificación OTP, **ALTO** retiene la transacción y la escala a un analista humano. El modelo nunca bloquea una cuenta por sí solo.
- Explica cada alerta con las variables más desviadas y guarda métricas, gráficos, alertas y bitácora en `salidas/`.

## Cómo ejecutarlo

Requiere Python 3.10 o superior. Desde la raíz del proyecto:

```bash
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m deteccion_fraude                           # entrena, evalúa y genera las alertas en ./salidas
```

Otros modos:

```bash
python -m deteccion_fraude --demo --demo-n 20 --pausa 0.8 --sin-graficos   # simula transacciones llegando en vivo
python -m deteccion_fraude --modelo iforest                                 # solo Isolation Forest
python -m deteccion_fraude --csv creditcard.csv                             # usar el dataset de Kaggle
python -m deteccion_fraude --salidas resultados                             # otra carpeta de salida
python -m unittest discover -s tests -v                                     # pruebas
```

Opciones: `--n` (cantidad de transacciones), `--fraude` (proporción de fraude), `--presupuesto` (fracción revisada por analistas, define el nivel ALTO), `--presupuesto-medio` (fracción con OTP), `--semilla`.

También puede instalarse como paquete (`pip install -e .`), lo que deja disponible el comando `detectar-fraude` con las mismas opciones.

## Estructura

```
.
├── deteccion_fraude/       paquete principal
│   ├── __main__.py         permite `python -m deteccion_fraude`
│   ├── main.py             pipeline completo y modo --demo
│   ├── datos.py            generación / carga de transacciones
│   ├── modelo.py           Isolation Forest y Autoencoder
│   ├── evaluacion.py       métricas y gráficos
│   └── alertas.py          niveles de alerta, explicaciones y bitácora
├── tests/
│   └── test_basico.py      pruebas unitarias
├── pyproject.toml          metadatos e instalación del paquete
└── requirements.txt        dependencias
```
