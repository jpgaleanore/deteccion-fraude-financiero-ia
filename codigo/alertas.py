# -*- coding: utf-8 -*-
"""
alertas.py - Sistema de alertas con niveles y supervisión humana.

Aquí está la respuesta de diseño al eje ético del proyecto ("falsos positivos
que congelan recursos a usuarios legítimos sin previo aviso"). El modelo NUNCA
bloquea una cuenta por sí solo. La puntuación de anomalía se traduce en tres
niveles con acciones proporcionales:

    BAJO   (score < umbral_medio)  Se aprueba y se registra.
    MEDIO  (umbral_medio ≤ s < umbral_alto)
           Se aprueba pero se pide verificación adicional al cliente
           (notificación push / OTP). Si el cliente confirma, la alerta se
           cierra y el modelo "aprende" que ese patrón era legítimo.
    ALTO   (s ≥ umbral_alto)
           Se RETIENE solo esa transacción (no la cuenta), se avisa al
           cliente de inmediato por el canal registrado y se crea un caso
           para un analista humano con un plazo máximo de revisión (SLA).
           El bloqueo de la cuenta solo ocurre si el analista lo confirma o
           si el cliente declara que no reconoce la operación.

Toda decisión queda en una bitácora (log) con: identificador, puntuación,
nivel, acción, motivos explicables y estado de revisión. Esto responde a los
principios de transparencia, explicabilidad, responsabilidad y derecho a
réplica (Ley 1581 de 2012, Ley 1266 de 2008, Recomendación UNESCO 2021).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from datos import NOMBRES_LEGIBLES

ACCIONES = {
    "BAJO": "Aprobar y registrar",
    "MEDIO": "Aprobar con verificación OTP/push al cliente",
    "ALTO": "Retener transacción, avisar al cliente y escalar a analista humano (SLA 2 h)",
}


@dataclass
class Umbrales:
    medio: float   # inicio del nivel MEDIO
    alto: float    # inicio del nivel ALTO

    @staticmethod
    def desde_presupuesto(scores_entrenamiento: np.ndarray, presupuesto_medio: float = 0.03,
                          presupuesto_alto: float = 0.01) -> "Umbrales":
        """Umbrales por capacidad operativa: % de transacciones que pasan a cada nivel."""
        return Umbrales(medio=float(np.quantile(scores_entrenamiento, 1 - presupuesto_medio)),
                        alto=float(np.quantile(scores_entrenamiento, 1 - presupuesto_alto)))


class SistemaAlertas:
    def __init__(self, umbrales: Umbrales, columnas: list[str], referencia: pd.DataFrame,
                 max_alertas_altas_por_cliente: int = 2) -> None:
        self.umbrales = umbrales
        self.columnas = columnas
        # Media y desviación de la población legítima para explicar cada alerta.
        self._media = referencia[columnas].mean()
        self._std = referencia[columnas].std().replace(0, 1)
        self.max_alertas_altas = max_alertas_altas_por_cliente
        self.bitacora: list[dict] = []
        self._altas_por_cliente: dict = {}

    # ---- clasificación ------------------------------------------------------------------------
    def nivel(self, score: float) -> str:
        if score >= self.umbrales.alto:
            return "ALTO"
        if score >= self.umbrales.medio:
            return "MEDIO"
        return "BAJO"

    def explicar(self, fila: pd.Series, top: int = 3) -> str:
        """Las `top` variables más alejadas de lo normal (z-score), en lenguaje claro."""
        z = ((fila[self.columnas] - self._media) / self._std).astype(float)
        z = z.reindex(z.abs().sort_values(ascending=False).index)
        partes = []
        for col, val in z.head(top).items():
            if abs(val) < 1.0:
                continue
            direccion = "muy alto" if val > 0 else "muy bajo"
            valor = float(fila[col])
            texto_valor = f"{valor:,.0f}" if abs(valor) >= 1000 else f"{valor:g}"
            partes.append(f"{NOMBRES_LEGIBLES.get(col, col)} {direccion} ({texto_valor})")
        return "; ".join(partes) if partes else "patrón global poco frecuente"

    # ---- procesamiento ------------------------------------------------------------------------
    def procesar(self, fila: pd.Series, score: float) -> dict:
        nivel = self.nivel(score)
        accion = ACCIONES[nivel]
        cliente = fila.get("cliente_id", "desconocido")
        bloqueo_cuenta = False
        if nivel == "ALTO":
            self._altas_por_cliente[cliente] = self._altas_por_cliente.get(cliente, 0) + 1
            if self._altas_por_cliente[cliente] >= self.max_alertas_altas:
                bloqueo_cuenta = True
                accion += " · Varias alertas altas: se propone bloqueo PREVENTIVO de la cuenta, sujeto a confirmación del analista y aviso al cliente"
        registro = {
            "tx_id": fila.get("tx_id", ""),
            "fecha_hora": str(fila.get("fecha_hora", "")),
            "cliente_id": cliente,
            "monto": float(fila.get("monto", 0)),
            "score": round(float(score), 4),
            "nivel": nivel,
            "accion": accion,
            "motivos": self.explicar(fila) if nivel != "BAJO" else "",
            "propone_bloqueo_cuenta": bloqueo_cuenta,
            "requiere_revision_humana": nivel == "ALTO",
            "estado": "PENDIENTE ANALISTA" if nivel == "ALTO" else ("PENDIENTE CLIENTE" if nivel == "MEDIO" else "CERRADA"),
            "registrado_en": datetime.now().isoformat(timespec="seconds"),
        }
        self.bitacora.append(registro)
        return registro

    def procesar_lote(self, df: pd.DataFrame, scores: np.ndarray) -> pd.DataFrame:
        for (_, fila), s in zip(df.iterrows(), scores):
            self.procesar(fila, s)
        return self.como_dataframe()

    def como_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.bitacora)

    def guardar(self, carpeta: Path) -> tuple[Path, Path]:
        carpeta.mkdir(parents=True, exist_ok=True)
        df = self.como_dataframe()
        ruta_alertas = carpeta / "alertas.csv"
        ruta_log = carpeta / "bitacora_decisiones.csv"
        df[df["nivel"] != "BAJO"].to_csv(ruta_alertas, index=False)
        df.to_csv(ruta_log, index=False)
        return ruta_alertas, ruta_log

    def resumen(self) -> pd.Series:
        df = self.como_dataframe()
        return df["nivel"].value_counts().reindex(["BAJO", "MEDIO", "ALTO"]).fillna(0).astype(int)
