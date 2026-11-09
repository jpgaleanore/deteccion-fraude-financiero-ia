# -*- coding: utf-8 -*-
"""
evaluacion.py - Métricas y gráficos para datasets desbalanceados.

Con 0,5 % de fraude la exactitud (accuracy) engaña: un modelo que diga
"todo es legítimo" acierta el 99,5 %. Por eso se reportan:

    AUC-ROC            Capacidad de ordenar fraudes por encima de legítimas.
    AUC-PR (AP)        Precisión promedio; es la métrica honesta con clases raras.
    Precisión          De lo que alerto, cuánto es fraude de verdad.
    Recall             De los fraudes reales, cuántos detecto.
    F1                 Balance entre las dos anteriores.
    Falsos positivos   Clientes legítimos afectados: el costo ético del sistema.

El umbral se fija por "presupuesto de alertas": el porcentaje de transacciones
que el equipo de analistas puede revisar por día (p. ej. 1 %). Esto evita
tener que conocer las etiquetas para operar y hace explícito el costo humano.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (average_precision_score, confusion_matrix, precision_recall_curve,
                             roc_auc_score)


@dataclass
class Resultado:
    modelo: str
    umbral: float
    auc_roc: float
    auc_pr: float
    precision: float
    recall: float
    f1: float
    verdaderos_positivos: int
    falsos_positivos: int
    falsos_negativos: int
    verdaderos_negativos: int
    segundos_entrenamiento: float

    def como_fila(self) -> dict:
        return asdict(self)


def umbral_por_presupuesto(scores: np.ndarray, presupuesto: float) -> float:
    """Umbral tal que solo el `presupuesto` (fracción) de transacciones genera alerta."""
    return float(np.quantile(scores, 1 - presupuesto))


def evaluar(nombre: str, y_real: np.ndarray, scores: np.ndarray, umbral: float,
            segundos: float = 0.0) -> Resultado:
    y_pred = (scores >= umbral).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_real, y_pred, labels=[0, 1]).ravel()
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return Resultado(
        modelo=nombre, umbral=round(umbral, 4),
        auc_roc=round(float(roc_auc_score(y_real, scores)), 4),
        auc_pr=round(float(average_precision_score(y_real, scores)), 4),
        precision=round(precision, 4), recall=round(recall, 4), f1=round(f1, 4),
        verdaderos_positivos=int(tp), falsos_positivos=int(fp), falsos_negativos=int(fn),
        verdaderos_negativos=int(tn), segundos_entrenamiento=round(segundos, 2),
    )


def tabla_resultados(resultados: list[Resultado]) -> pd.DataFrame:
    return pd.DataFrame([r.como_fila() for r in resultados]).set_index("modelo")


def recall_por_tipo(df: pd.DataFrame, columna_alerta: str) -> pd.DataFrame:
    """Qué patrón de fraude detecta mejor el modelo (card testing, toma de cuenta, clonación)."""
    fr = df[df["es_fraude"] == 1]
    if fr.empty or "tipo_fraude" not in fr:
        return pd.DataFrame()
    g = fr.groupby("tipo_fraude")[columna_alerta].agg(["sum", "count"])
    g["recall"] = (g["sum"] / g["count"]).round(3)
    return g.rename(columns={"sum": "detectados", "count": "total"})


def graficar(df: pd.DataFrame, scores: dict[str, np.ndarray], umbrales: dict[str, float],
             carpeta: Path) -> list[Path]:
    """Genera los gráficos para el video. Devuelve las rutas creadas."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    carpeta.mkdir(parents=True, exist_ok=True)
    y = df["es_fraude"].to_numpy()
    rutas = []
    azul, rojo, gris = "#1F3A5F", "#C62828", "#8A8A9A"

    # 1. Desbalance de clases
    fig, ax = plt.subplots(figsize=(5, 3.2))
    conteo = df["es_fraude"].value_counts().sort_index()
    ax.bar(["Legítimas", "Fraude"], conteo.values, color=[azul, rojo])
    for i, v in enumerate(conteo.values):
        ax.text(i, v, f"{v:,}\n({v / len(df):.2%})", ha="center", va="bottom", fontsize=9)
    ax.set_title("Desbalance del conjunto de datos")
    ax.set_ylabel("Transacciones")
    ax.set_yscale("log")
    fig.tight_layout()
    rutas.append(carpeta / "01_desbalance.png")
    fig.savefig(rutas[-1], dpi=150)
    plt.close(fig)

    # 2. Distribución de puntuaciones por clase (un panel por modelo)
    fig, axes = plt.subplots(1, len(scores), figsize=(5 * len(scores), 3.4), squeeze=False)
    for ax, (nombre, s) in zip(axes[0], scores.items()):
        ax.hist(s[y == 0], bins=50, color=azul, alpha=0.7, label="Legítimas", density=True)
        ax.hist(s[y == 1], bins=50, color=rojo, alpha=0.7, label="Fraude", density=True)
        ax.axvline(umbrales[nombre], color="black", ls="--", lw=1, label=f"Umbral {umbrales[nombre]:.3f}")
        ax.set_title(f"Puntuación de anomalía · {nombre}")
        ax.set_xlabel("Puntuación (0 = normal, 1 = muy anómala)")
        ax.set_yscale("log")
        ax.legend(fontsize=8)
    fig.tight_layout()
    rutas.append(carpeta / "02_puntuaciones.png")
    fig.savefig(rutas[-1], dpi=150)
    plt.close(fig)

    # 3. Curva precisión-recall
    fig, ax = plt.subplots(figsize=(5, 3.6))
    for (nombre, s), color in zip(scores.items(), [azul, rojo, gris]):
        p, r, _ = precision_recall_curve(y, s)
        ax.plot(r, p, color=color, label=f"{nombre} (AP={average_precision_score(y, s):.2f})")
    ax.axhline(y.mean(), color=gris, ls=":", label=f"Azar ({y.mean():.3f})")
    ax.set_xlabel("Recall (fraudes detectados)")
    ax.set_ylabel("Precisión (alertas correctas)")
    ax.set_title("Curva precisión-recall")
    ax.legend(fontsize=8)
    fig.tight_layout()
    rutas.append(carpeta / "03_precision_recall.png")
    fig.savefig(rutas[-1], dpi=150)
    plt.close(fig)

    # 4. Matrices de confusión
    fig, axes = plt.subplots(1, len(scores), figsize=(4.2 * len(scores), 3.6), squeeze=False)
    for ax, (nombre, s) in zip(axes[0], scores.items()):
        cm = confusion_matrix(y, (s >= umbrales[nombre]).astype(int), labels=[0, 1])
        ax.imshow(cm, cmap="Blues")
        for (i, j), v in np.ndenumerate(cm):
            ax.text(j, i, f"{v:,}", ha="center", va="center",
                    color="white" if v > cm.max() / 2 else "black", fontsize=11)
        ax.set_xticks([0, 1], ["Sin alerta", "Alerta"])
        ax.set_yticks([0, 1], ["Legítima", "Fraude"])
        ax.set_title(f"Matriz de confusión · {nombre}")
        ax.set_xlabel("Decisión del sistema")
        ax.set_ylabel("Realidad")
    fig.tight_layout()
    rutas.append(carpeta / "04_matriz_confusion.png")
    fig.savefig(rutas[-1], dpi=150)
    plt.close(fig)
    return rutas
