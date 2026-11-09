# -*- coding: utf-8 -*-
"""
datos.py - Generación y carga del conjunto de transacciones.

Produce un conjunto de datos sintético, reproducible y ALTAMENTE DESBALANCEADO
(≈0,5 % de fraude) que imita el comportamiento de transacciones bancarias en
Colombia. No se usan datos reales de ninguna persona: todo se genera con un
generador de números aleatorios con semilla fija, por lo que el experimento
es repetible.

Cada transacción tiene estas variables (las que usa el modelo están en
COLUMNAS_MODELO):

    monto              Valor en pesos colombianos (COP).
    hora               Hora del día (0-23).
    fin_de_semana      1 si es sábado o domingo.
    distancia_km       Distancia entre la transacción y la ubicación habitual
                       del cliente.
    tx_ultima_hora     Cantidad de transacciones del mismo cliente en la
                       última hora (velocidad).
    ratio_monto        Monto / promedio histórico del cliente.
    pais_distinto      1 si la transacción ocurre fuera de Colombia.
    dispositivo_nuevo  1 si se usa un dispositivo nunca visto para el cliente.
    comercio_nuevo     1 si el cliente nunca había comprado en ese comercio.
    intentos_pin       Intentos fallidos de PIN/OTP antes de aprobar.
    canal              0 = datáfono, 1 = app, 2 = web, 3 = cajero.

    es_fraude          Etiqueta real (1 = fraude). SOLO se usa para evaluar;
                       el modelo nunca la ve al entrenar (aprendizaje no
                       supervisado).
    tipo_fraude        Patrón simulado: card_testing, toma_de_cuenta,
                       tarjeta_clonada, fraude_sutil o "" si es legítima.

También puede cargar el dataset público de Kaggle "Credit Card Fraud
Detection" (creditcard.csv) si se pasa la ruta con --csv; en ese caso las
columnas del modelo son V1..V28, Amount y Time.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

COLUMNAS_MODELO = [
    "monto", "hora", "fin_de_semana", "distancia_km", "tx_ultima_hora",
    "ratio_monto", "pais_distinto", "dispositivo_nuevo", "comercio_nuevo",
    "intentos_pin", "canal",
]

NOMBRES_LEGIBLES = {
    "monto": "monto de la transacción",
    "hora": "hora del día",
    "fin_de_semana": "fin de semana",
    "distancia_km": "distancia a la ubicación habitual",
    "tx_ultima_hora": "transacciones en la última hora",
    "ratio_monto": "monto frente al promedio del cliente",
    "pais_distinto": "transacción fuera del país",
    "dispositivo_nuevo": "dispositivo nunca visto",
    "comercio_nuevo": "comercio nuevo para el cliente",
    "intentos_pin": "intentos fallidos de PIN/OTP",
    "canal": "canal de la transacción",
}


def _legitimas(rng: np.random.Generator, n: int, n_clientes: int) -> pd.DataFrame:
    """Transacciones normales: montos lognormales, horas diurnas, cerca de casa."""
    cliente = rng.integers(0, n_clientes, n)
    promedio_cliente = rng.lognormal(mean=11.3, sigma=0.5, size=n_clientes)  # ≈ 80.000 COP
    monto = rng.lognormal(mean=0.0, sigma=0.6, size=n) * promedio_cliente[cliente]
    hora = np.clip(rng.normal(14, 4.5, n), 0, 23).round().astype(int)
    fin_de_semana = (rng.random(n) < 2 / 7).astype(int)
    distancia_km = np.abs(rng.exponential(scale=6, size=n))
    tx_ultima_hora = rng.poisson(0.4, n)
    # Clientes que viajan (legítimo, pero se parece a una tarjeta clonada).
    pais_distinto = (rng.random(n) < 0.015).astype(int)
    distancia_km = np.where(pais_distinto == 1, rng.uniform(800, 6000, n), distancia_km)
    # Compras grandes legítimas (electrodomésticos, matrículas, viajes): 2 % de los casos.
    compra_grande = rng.random(n) < 0.02
    monto = np.where(compra_grande, monto * rng.uniform(4, 12, n), monto)
    dispositivo_nuevo = (rng.random(n) < 0.03).astype(int)
    comercio_nuevo = (rng.random(n) < 0.20).astype(int)
    intentos_pin = rng.choice([0, 1, 2], size=n, p=[0.93, 0.06, 0.01])
    canal = rng.choice([0, 1, 2, 3], size=n, p=[0.45, 0.35, 0.12, 0.08])
    return pd.DataFrame({
        "cliente_id": cliente,
        "monto": monto.round(0),
        "hora": hora,
        "fin_de_semana": fin_de_semana,
        "distancia_km": distancia_km.round(1),
        "tx_ultima_hora": tx_ultima_hora,
        "ratio_monto": (monto / promedio_cliente[cliente]).round(2),
        "pais_distinto": pais_distinto,
        "dispositivo_nuevo": dispositivo_nuevo,
        "comercio_nuevo": comercio_nuevo,
        "intentos_pin": intentos_pin,
        "canal": canal,
        "es_fraude": 0,
        "tipo_fraude": "",
    })


def _fraudes(rng: np.random.Generator, n: int, n_clientes: int) -> pd.DataFrame:
    """Tres patrones de fraude documentados por la Superfinanciera y Asobancaria."""
    tipos = rng.choice(["card_testing", "toma_de_cuenta", "tarjeta_clonada", "fraude_sutil"],
                       size=n, p=[0.28, 0.27, 0.25, 0.20])
    filas = []
    for t in tipos:
        cliente = int(rng.integers(0, n_clientes))
        if t == "card_testing":
            # Muchos micro-cobros seguidos desde un dispositivo nuevo, por web.
            fila = dict(monto=rng.uniform(1000, 15000), hora=rng.integers(0, 24),
                        distancia_km=rng.uniform(5, 60), tx_ultima_hora=rng.integers(6, 25),
                        ratio_monto=rng.uniform(0.02, 0.2), pais_distinto=int(rng.random() < 0.3),
                        dispositivo_nuevo=1, comercio_nuevo=1, intentos_pin=rng.integers(0, 3),
                        canal=2)
        elif t == "toma_de_cuenta":
            # Robo de credenciales: monto grande, madrugada, app en dispositivo nuevo,
            # varios intentos de OTP.
            fila = dict(monto=rng.uniform(900_000, 6_000_000), hora=rng.choice([0, 1, 2, 3, 4, 23]),
                        distancia_km=rng.uniform(20, 400), tx_ultima_hora=rng.integers(2, 6),
                        ratio_monto=rng.uniform(6, 40), pais_distinto=int(rng.random() < 0.4),
                        dispositivo_nuevo=1, comercio_nuevo=int(rng.random() < 0.9),
                        intentos_pin=rng.integers(2, 6), canal=rng.choice([1, 2]))
        elif t == "fraude_sutil":
            # Defraudador que conoce los controles: montos pequeños, horario normal,
            # cerca del cliente, dispositivo conocido. Solo lo delatan señales débiles.
            fila = dict(monto=rng.uniform(20_000, 200_000), hora=rng.integers(9, 21),
                        distancia_km=rng.uniform(2, 40), tx_ultima_hora=rng.integers(1, 4),
                        ratio_monto=rng.uniform(0.8, 3.0), pais_distinto=0,
                        dispositivo_nuevo=int(rng.random() < 0.5), comercio_nuevo=1,
                        intentos_pin=rng.integers(0, 2), canal=rng.choice([1, 2]))
        else:
            # Tarjeta clonada usada presencialmente lejos del cliente.
            fila = dict(monto=rng.uniform(150_000, 1_500_000), hora=rng.integers(0, 24),
                        distancia_km=rng.uniform(300, 9000), tx_ultima_hora=rng.integers(1, 4),
                        ratio_monto=rng.uniform(2, 15), pais_distinto=int(rng.random() < 0.7),
                        dispositivo_nuevo=0, comercio_nuevo=1, intentos_pin=rng.integers(0, 2),
                        canal=rng.choice([0, 3]))
        fila.update(cliente_id=cliente, fin_de_semana=int(rng.random() < 2 / 7),
                    es_fraude=1, tipo_fraude=t)
        filas.append(fila)
    df = pd.DataFrame(filas)
    df["monto"] = df["monto"].round(0)
    df["distancia_km"] = df["distancia_km"].round(1)
    df["ratio_monto"] = df["ratio_monto"].round(2)
    return df


def generar_transacciones(n: int = 60_000, proporcion_fraude: float = 0.005,
                          n_clientes: int = 4_000, semilla: int = 42) -> pd.DataFrame:
    """Devuelve un DataFrame mezclado con `n` transacciones y ≈ proporcion_fraude de fraudes."""
    rng = np.random.default_rng(semilla)
    n_fraude = max(1, int(round(n * proporcion_fraude)))
    df = pd.concat([_legitimas(rng, n - n_fraude, n_clientes), _fraudes(rng, n_fraude, n_clientes)],
                   ignore_index=True)
    df = df.sample(frac=1.0, random_state=semilla).reset_index(drop=True)
    df.insert(0, "tx_id", [f"TX{i:07d}" for i in range(len(df))])
    inicio = pd.Timestamp("2026-10-01 00:00:00")
    df.insert(1, "fecha_hora", inicio + pd.to_timedelta(np.arange(len(df)) * (30 * 24 * 60 / len(df)), unit="min"))
    df = df[["tx_id", "fecha_hora", "cliente_id"] + COLUMNAS_MODELO + ["es_fraude", "tipo_fraude"]]
    return df


def cargar_csv(ruta: str) -> tuple[pd.DataFrame, list[str]]:
    """Carga un CSV propio o el de Kaggle (creditcard.csv). Devuelve (df, columnas_del_modelo)."""
    df = pd.read_csv(ruta)
    if "Class" in df.columns:  # formato Kaggle
        df = df.rename(columns={"Class": "es_fraude"})
        columnas = [c for c in df.columns if c.startswith("V")] + ["Amount", "Time"]
        df["tipo_fraude"] = np.where(df["es_fraude"] == 1, "kaggle", "")
        if "tx_id" not in df.columns:
            df.insert(0, "tx_id", [f"TX{i:07d}" for i in range(len(df))])
        return df, columnas
    faltantes = [c for c in COLUMNAS_MODELO if c not in df.columns]
    if faltantes:
        raise ValueError(f"Al CSV le faltan columnas: {faltantes}")
    return df, COLUMNAS_MODELO


if __name__ == "__main__":
    d = generar_transacciones()
    print(d.head())
    print(f"\n{len(d):,} transacciones, {int(d.es_fraude.sum())} fraudes "
          f"({d.es_fraude.mean():.2%}).")
    print(d.loc[d.es_fraude == 1, "tipo_fraude"].value_counts())
