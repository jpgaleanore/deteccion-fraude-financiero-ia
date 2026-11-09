# -*- coding: utf-8 -*-
"""
decision.py - Un modelo entrenado que decide sobre transacciones nuevas.

`DecisorFraude` empaqueta todo lo que el sistema aprendió y necesita para
decidir: el detector (Isolation Forest o Autoencoder con su escalador y sus
puntuaciones de entrenamiento), los umbrales de los niveles y el sistema de
alertas con las medias de la población legítima para explicar los motivos.

Se puede guardar en disco con pickle y cargar después sin volver a entrenar:

    decisor.guardar("modelo_fraude.pkl")
    decisor = DecisorFraude.cargar("modelo_fraude.pkl")
    decisor.decidir({"monto": 5_900_000, "hora": 1, "intentos_pin": 4, "dispositivo_nuevo": 1})

Las variables que no se indiquen toman el valor de una compra típica
(VALORES_TIPICOS); si se da el monto y no el ratio, el ratio se calcula
frente al gasto promedio de la población.
"""
from __future__ import annotations

import pickle
from pathlib import Path

import pandas as pd

from .alertas import SistemaAlertas, Umbrales
from .datos import COLUMNAS_MODELO
from .modelo import DetectorBase

GASTO_PROMEDIO_POBLACION = 125_000  # COP, media de las transacciones legítimas sintéticas

VALORES_TIPICOS = {
    "monto": 80_000, "hora": 14, "fin_de_semana": 0, "distancia_km": 5.0, "tx_ultima_hora": 0,
    "ratio_monto": None, "pais_distinto": 0, "dispositivo_nuevo": 0, "comercio_nuevo": 0,
    "intentos_pin": 0, "canal": 1,
}

ALIAS = {  # nombres cortos aceptados en la línea de comandos
    "pais": "pais_distinto", "dispositivo": "dispositivo_nuevo", "comercio": "comercio_nuevo",
    "pin": "intentos_pin", "distancia": "distancia_km", "velocidad": "tx_ultima_hora",
    "ratio": "ratio_monto", "finde": "fin_de_semana",
}


def transaccion_desde_texto(texto: str) -> dict:
    """'monto=5900000,hora=1,pin=4,dispositivo=1' -> dict completo con las 11 variables."""
    valores = dict(VALORES_TIPICOS)
    for par in filter(None, (p.strip() for p in texto.split(","))):
        if "=" not in par:
            raise ValueError(f"Par inválido '{par}'. Use variable=valor, p. ej. monto=5900000")
        k, v = (x.strip() for x in par.split("=", 1))
        k = ALIAS.get(k, k)
        if k not in COLUMNAS_MODELO:
            raise ValueError(f"Variable desconocida '{k}'. Válidas: {', '.join(COLUMNAS_MODELO)}")
        valores[k] = float(v)
    if valores["ratio_monto"] is None:
        valores["ratio_monto"] = round(valores["monto"] / GASTO_PROMEDIO_POBLACION, 2)
    return valores


class DecisorFraude:
    def __init__(self, detector: DetectorBase, umbrales: Umbrales, sistema: SistemaAlertas,
                 columnas: list[str] = COLUMNAS_MODELO) -> None:
        self.detector = detector
        self.umbrales = umbrales
        self.sistema = sistema
        self.columnas = columnas

    # ---- persistencia -------------------------------------------------------------------------
    def guardar(self, ruta: str | Path) -> Path:
        ruta = Path(ruta)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        with open(ruta, "wb") as f:
            pickle.dump(self, f)
        return ruta

    @staticmethod
    def cargar(ruta: str | Path) -> "DecisorFraude":
        with open(ruta, "rb") as f:
            obj = pickle.load(f)  # archivo propio, generado por este mismo programa
        if not isinstance(obj, DecisorFraude):
            raise TypeError("El archivo no contiene un DecisorFraude")
        return obj

    # ---- decisión -----------------------------------------------------------------------------
    def puntuar(self, transaccion: dict) -> float:
        fila = pd.DataFrame([{c: transaccion.get(c, VALORES_TIPICOS[c]) for c in self.columnas}])
        return float(self.detector.puntuar(fila)[0])

    def decidir(self, transaccion: dict, tx_id: str = "MANUAL", cliente_id="manual") -> dict:
        """Devuelve el registro de la bitácora: score, nivel, acción y motivos."""
        completa = {c: transaccion.get(c, VALORES_TIPICOS[c]) for c in self.columnas}
        if completa["ratio_monto"] is None:
            completa["ratio_monto"] = completa["monto"] / GASTO_PROMEDIO_POBLACION
        score = self.puntuar(completa)
        fila = pd.Series({**completa, "tx_id": tx_id, "cliente_id": cliente_id, "fecha_hora": ""})
        return self.sistema.procesar(fila, score)

    def decidir_lote(self, df: pd.DataFrame) -> pd.DataFrame:
        """Decide sobre un DataFrame con las columnas del modelo (p. ej. un CSV nuevo)."""
        faltantes = [c for c in self.columnas if c not in df.columns]
        if faltantes:
            raise ValueError(f"Faltan columnas: {faltantes}")
        scores = self.detector.puntuar(df[self.columnas])
        registros = [self.sistema.procesar(fila, s) for (_, fila), s in zip(df.iterrows(), scores)]
        return pd.DataFrame(registros)
