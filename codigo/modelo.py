# -*- coding: utf-8 -*-
"""
modelo.py - Detectores de anomalías no supervisados.

Se implementan dos técnicas vistas en la unidad de Aprendizaje de Máquinas,
con la misma interfaz (entrenar / puntuar) para poder compararlas:

1. IsolationForest (Liu, Ting & Zhou, 2008). Construye árboles que aíslan
   observaciones al azar; las anomalías se aíslan en pocos cortes, así que
   su "profundidad media" es corta. No necesita etiquetas: es ideal cuando el
   fraude es < 1 % de los datos y no hay suficientes casos para un clasificador.

2. Autoencoder. Red neuronal que aprende a comprimir y reconstruir las
   transacciones normales. Una transacción fraudulenta se reconstruye mal, y
   ese error de reconstrucción es la puntuación de anomalía. Se implementa con
   MLPRegressor de scikit-learn (entrada == salida) para no depender de
   PyTorch/TensorFlow y poder ejecutarse en cualquier equipo del curso.

En ambos casos la puntuación devuelta es "a mayor valor, más sospechosa",
normalizada entre 0 y 1 (percentil sobre los datos de entrenamiento) para que
el sistema de alertas (alertas.py) pueda usar los mismos umbrales.
"""
from __future__ import annotations

import time

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler


class DetectorBase:
    nombre = "base"

    def __init__(self) -> None:
        self.scaler = StandardScaler()
        self._scores_entrenamiento: np.ndarray | None = None
        self.segundos_entrenamiento = 0.0

    # Las subclases implementan estos dos métodos.
    def _entrenar(self, X: np.ndarray) -> None:  # pragma: no cover - abstracto
        raise NotImplementedError

    def _puntuar_crudo(self, X: np.ndarray) -> np.ndarray:  # pragma: no cover - abstracto
        raise NotImplementedError

    def entrenar(self, X: pd.DataFrame | np.ndarray) -> "DetectorBase":
        t0 = time.perf_counter()
        Xs = self.scaler.fit_transform(np.asarray(X, dtype=float))
        self._entrenar(Xs)
        self._scores_entrenamiento = np.sort(self._puntuar_crudo(Xs))
        self.segundos_entrenamiento = time.perf_counter() - t0
        return self

    def puntuar(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """Puntuación de anomalía en [0, 1]: percentil respecto al entrenamiento."""
        Xs = self.scaler.transform(np.asarray(X, dtype=float))
        crudo = self._puntuar_crudo(Xs)
        pos = np.searchsorted(self._scores_entrenamiento, crudo, side="right")
        return pos / len(self._scores_entrenamiento)


class DetectorIsolationForest(DetectorBase):
    nombre = "Isolation Forest"

    def __init__(self, contaminacion: float = 0.005, n_arboles: int = 300, semilla: int = 42) -> None:
        super().__init__()
        self.modelo = IsolationForest(n_estimators=n_arboles, contamination=contaminacion,
                                      random_state=semilla, n_jobs=-1)

    def _entrenar(self, X: np.ndarray) -> None:
        self.modelo.fit(X)

    def _puntuar_crudo(self, X: np.ndarray) -> np.ndarray:
        # score_samples: valores más negativos = más anómalos. Se invierte el signo.
        return -self.modelo.score_samples(X)


class DetectorAutoencoder(DetectorBase):
    nombre = "Autoencoder"

    def __init__(self, capas: tuple[int, ...] = (8, 3, 8), epocas: int = 60, semilla: int = 42) -> None:
        super().__init__()
        self.modelo = MLPRegressor(hidden_layer_sizes=capas, activation="tanh", solver="adam",
                                   max_iter=epocas, random_state=semilla, early_stopping=False,
                                   learning_rate_init=1e-3)

    def _entrenar(self, X: np.ndarray) -> None:
        self.modelo.fit(X, X)  # aprende a reconstruir su propia entrada

    def _puntuar_crudo(self, X: np.ndarray) -> np.ndarray:
        reconstruido = self.modelo.predict(X)
        return np.mean((X - reconstruido) ** 2, axis=1)  # error cuadrático medio por fila


def crear_detector(nombre: str, contaminacion: float = 0.005, semilla: int = 42) -> DetectorBase:
    if nombre == "iforest":
        return DetectorIsolationForest(contaminacion=contaminacion, semilla=semilla)
    if nombre == "autoencoder":
        return DetectorAutoencoder(semilla=semilla)
    raise ValueError(f"Detector desconocido: {nombre}")
