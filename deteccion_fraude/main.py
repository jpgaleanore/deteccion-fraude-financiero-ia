#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py - Detección de fraude financiero y bloqueo responsable de cuentas.

Proyecto final · ISLPE05 Inteligencia Artificial (Línea Prof. II) · Grupo 8
Universidad Católica Luis Amigó · Inspiración: Ozark.

Flujo (modo normal):
    1. Generar (o cargar) transacciones altamente desbalanceadas.
    2. Dividir en entrenamiento (días 1-24) y operación (días 25-30).
    3. Entrenar Isolation Forest y Autoencoder SIN etiquetas.
    4. Evaluar contra la etiqueta real (solo para medir), con presupuesto de alertas.
    5. Pasar las transacciones de operación por el sistema de alertas con
       niveles (BAJO / MEDIO / ALTO) y supervisión humana.
    6. Guardar métricas, gráficos, alertas y bitácora en ../salidas/.

Uso (desde la raíz del proyecto):
    python -m deteccion_fraude                      # ejecución completa
    python -m deteccion_fraude --demo               # simula transacciones llegando en vivo (para el video)
    python -m deteccion_fraude --modelo iforest     # solo Isolation Forest
    python -m deteccion_fraude --csv creditcard.csv # usar el dataset público de Kaggle
    python -m deteccion_fraude --salidas resultados # cambiar la carpeta de salida
    python -m deteccion_fraude --guardar-modelo salidas/modelo_fraude.pkl
    python -m deteccion_fraude --cargar-modelo salidas/modelo_fraude.pkl \
        --transaccion "monto=5900000,hora=1,pin=4,dispositivo=1"   # decisión sobre una entrada propia
"""
from __future__ import annotations

import argparse
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from .alertas import SistemaAlertas, Umbrales
from .decision import DecisorFraude, transaccion_desde_texto
from .datos import COLUMNAS_MODELO, cargar_csv, generar_transacciones
from .evaluacion import evaluar, graficar, recall_por_tipo, tabla_resultados, umbral_por_presupuesto
from .modelo import crear_detector

warnings.filterwarnings("ignore")  # avisos de convergencia del autoencoder no aportan al usuario
LINEA = "─" * 78


def titulo(texto: str) -> None:
    print(f"\n{LINEA}\n{texto}\n{LINEA}")


def argumentos() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Detección de fraude con aprendizaje no supervisado.")
    p.add_argument("--n", type=int, default=60_000, help="transacciones sintéticas (defecto 60000)")
    p.add_argument("--fraude", type=float, default=0.005, help="proporción de fraude (defecto 0.005)")
    p.add_argument("--semilla", type=int, default=42)
    p.add_argument("--csv", type=str, default=None, help="ruta a un CSV propio o creditcard.csv de Kaggle")
    p.add_argument("--modelo", choices=["iforest", "autoencoder", "ambos"], default="ambos")
    p.add_argument("--presupuesto", type=float, default=0.01,
                   help="fracción de transacciones que el equipo puede revisar (nivel ALTO). Defecto 1 %%")
    p.add_argument("--presupuesto-medio", type=float, default=0.03,
                   help="fracción que recibe verificación OTP (nivel MEDIO). Defecto 3 %%")
    p.add_argument("--salidas", type=Path, default=Path("salidas"),
                   help="carpeta de resultados (defecto ./salidas)")
    p.add_argument("--sin-graficos", action="store_true")
    p.add_argument("--demo", action="store_true", help="simula la llegada de transacciones en vivo")
    p.add_argument("--guardar-modelo", type=Path, default=None, metavar="RUTA",
                   help="guarda el modelo entrenado y sus umbrales (p. ej. salidas/modelo_fraude.pkl)")
    p.add_argument("--cargar-modelo", type=Path, default=None, metavar="RUTA",
                   help="usa un modelo ya guardado en vez de entrenar")
    p.add_argument("--transaccion", action="append", default=[], metavar="VARS",
                   help='decide sobre una transacción escrita a mano, p. ej. "monto=5900000,hora=1,pin=4,dispositivo=1". '
                        "Se puede repetir. Variables no indicadas toman valores típicos.")
    p.add_argument("--decidir-csv", type=Path, default=None, metavar="ARCHIVO",
                   help="decide sobre todas las transacciones de un CSV con las 11 columnas del modelo")
    p.add_argument("--demo-n", type=int, default=40, help="transacciones a mostrar en el modo demo")
    p.add_argument("--pausa", type=float, default=0.35, help="segundos entre transacciones en demo")
    return p.parse_args()


def cargar(args: argparse.Namespace) -> tuple[pd.DataFrame, list[str]]:
    if args.csv:
        df, columnas = cargar_csv(args.csv)
        print(f"Cargado {args.csv}: {len(df):,} filas.")
    else:
        df, columnas = generar_transacciones(args.n, args.fraude, semilla=args.semilla), COLUMNAS_MODELO
        print(f"Generadas {len(df):,} transacciones sintéticas (semilla {args.semilla}).")
    return df, columnas


def dividir(df: pd.DataFrame, frac_entrenamiento: float = 0.8) -> tuple[pd.DataFrame, pd.DataFrame]:
    """División temporal: se entrena con el pasado y se opera sobre el futuro."""
    corte = int(len(df) * frac_entrenamiento)
    return df.iloc[:corte].copy(), df.iloc[corte:].copy()


def main() -> int:
    args = argumentos()
    SALIDAS = args.salidas.resolve()
    if args.cargar_modelo and (args.transaccion or args.decidir_csv):
        decisor = DecisorFraude.cargar(args.cargar_modelo)
        print(f"Modelo cargado de {args.cargar_modelo} ({decisor.detector.nombre}) · sin reentrenar.")
        return decidir_entradas(decisor, args, SALIDAS)
    titulo("1. DATOS")
    df, columnas = cargar(args)
    n_fraude = int(df["es_fraude"].sum())
    print(f"Fraudes reales: {n_fraude:,} de {len(df):,} ({df['es_fraude'].mean():.2%}) → dataset desbalanceado.")
    if "tipo_fraude" in df:
        print(df.loc[df.es_fraude == 1, "tipo_fraude"].value_counts().to_string())

    entren, oper = dividir(df)
    print(f"\nEntrenamiento: {len(entren):,} transacciones · Operación (días recientes): {len(oper):,}")

    titulo("2. ENTRENAMIENTO NO SUPERVISADO (sin etiquetas)")
    nombres = ["iforest", "autoencoder"] if args.modelo == "ambos" else [args.modelo]
    detectores, scores_entren, scores_oper, umbrales, resultados = {}, {}, {}, {}, []
    for nombre in nombres:
        det = crear_detector(nombre, contaminacion=args.fraude, semilla=args.semilla)
        det.entrenar(entren[columnas])
        detectores[det.nombre] = det
        scores_entren[det.nombre] = det.puntuar(entren[columnas])
        scores_oper[det.nombre] = det.puntuar(oper[columnas])
        umbrales[det.nombre] = umbral_por_presupuesto(scores_entren[det.nombre], args.presupuesto)
        print(f"{det.nombre:<17} entrenado en {det.segundos_entrenamiento:5.2f} s · "
              f"umbral ALTO (revisa el {args.presupuesto:.1%} más anómalo) = {umbrales[det.nombre]:.4f}")

    titulo("3. EVALUACIÓN SOBRE OPERACIÓN (la etiqueta solo se usa para medir)")
    y = oper["es_fraude"].to_numpy()
    for nombre, det in detectores.items():
        r = evaluar(nombre, y, scores_oper[nombre], umbrales[nombre], det.segundos_entrenamiento)
        resultados.append(r)
        oper[f"alerta_{nombre}"] = (scores_oper[nombre] >= umbrales[nombre]).astype(int)
    tabla = tabla_resultados(resultados)
    pd.set_option("display.width", 160)
    print(tabla[["auc_roc", "auc_pr", "precision", "recall", "f1", "verdaderos_positivos",
                 "falsos_positivos", "falsos_negativos", "segundos_entrenamiento"]].to_string())
    print("\nLectura: AUC-PR es la métrica honesta con 0,5 % de fraude (el azar daría ≈ "
          f"{y.mean():.3f}). Los falsos positivos son clientes legítimos que recibirían una alerta: ese es el costo ético.")
    mejor = tabla["auc_pr"].idxmax()
    print(f"\nModelo principal elegido: {mejor} (mayor AUC-PR).")
    if "tipo_fraude" in oper:
        print(f"\nRecall por patrón de fraude · {mejor}:")
        print(recall_por_tipo(oper, f"alerta_{mejor}").to_string())

    SALIDAS.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(SALIDAS / "metricas.csv")
    if not args.sin_graficos:
        rutas = graficar(oper, scores_oper, umbrales, SALIDAS / "graficos")
        print("\nGráficos guardados:", ", ".join(r.name for r in rutas))

    titulo("4. SISTEMA DE ALERTAS CON NIVELES Y REVISIÓN HUMANA")
    umb = Umbrales.desde_presupuesto(scores_entren[mejor], args.presupuesto_medio, args.presupuesto)
    sistema = SistemaAlertas(umb, columnas, referencia=entren[entren["es_fraude"] == 0] if "es_fraude" in entren else entren)
    print(f"Umbral MEDIO = {umb.medio:.4f} (verificación OTP) · Umbral ALTO = {umb.alto:.4f} (analista humano)")
    decisor = DecisorFraude(detectores[mejor], umb, sistema, columnas)
    if args.guardar_modelo:
        ruta = decisor.guardar(args.guardar_modelo)
        print(f"Modelo guardado en {ruta} (detector, escalador, umbrales y sistema de alertas).")
    if args.transaccion or args.decidir_csv:
        return decidir_entradas(decisor, args, SALIDAS)

    if args.demo:
        demo_en_vivo(oper, scores_oper[mejor], sistema, args.demo_n, args.pausa)
    else:
        sistema.procesar_lote(oper, scores_oper[mejor])

    bit = sistema.como_dataframe()
    res = sistema.resumen()
    print(f"\nTransacciones procesadas: {len(bit):,}")
    for nivel, cnt in res.items():
        print(f"  {nivel:<6} {cnt:>7,}  → {ACCION_CORTA[nivel]}")
    if "es_fraude" in oper and len(bit) == len(oper):
        cruce = pd.crosstab(bit["nivel"].to_numpy(), oper["es_fraude"].to_numpy(),
                            rownames=["nivel"], colnames=["es_fraude"])
        print("\nNivel asignado vs. realidad (0 = legítima, 1 = fraude):")
        print(cruce.reindex(["BAJO", "MEDIO", "ALTO"]).fillna(0).astype(int).to_string())
    propuestas = int(bit["propone_bloqueo_cuenta"].sum())
    print(f"\nPropuestas de bloqueo de cuenta (siempre sujetas a confirmación humana): {propuestas}")
    ruta_alertas, ruta_log = sistema.guardar(SALIDAS)
    print(f"Alertas: {ruta_alertas}\nBitácora completa: {ruta_log}")

    altas = bit[bit["nivel"] == "ALTO"].head(3)
    if not altas.empty:
        print("\nEjemplo de alertas ALTAS explicadas:")
        for _, a in altas.iterrows():
            print(f"  · {a['tx_id']} cliente {a['cliente_id']} · ${a['monto']:,.0f} COP · score {a['score']:.3f}\n"
                  f"    motivos: {a['motivos']}\n    acción: {a['accion']}")
    titulo("FIN · Resultados en " + str(SALIDAS))
    return 0


def decidir_entradas(decisor: DecisorFraude, args: argparse.Namespace, salidas: Path) -> int:
    """Decide sobre las transacciones dadas con --transaccion y/o --decidir-csv."""
    titulo("DECISIÓN SOBRE TRANSACCIONES NUEVAS")
    print(f"Umbral MEDIO = {decisor.umbrales.medio:.4f} · Umbral ALTO = {decisor.umbrales.alto:.4f}\n")
    for i, texto in enumerate(args.transaccion, start=1):
        tx = transaccion_desde_texto(texto)
        reg = decisor.decidir(tx, tx_id=f"MANUAL{i:02d}")
        c = COLOR[reg["nivel"]]
        print(f"Transacción {i}: " + ", ".join(f"{k}={v:g}" for k, v in tx.items()))
        print(f"  score {reg['score']:.4f} → nivel {c}{reg['nivel']}{COLOR['fin']} · {ACCION_CORTA[reg['nivel']]}")
        if reg["motivos"]:
            print(f"  motivos: {reg['motivos']}")
        print(f"  acción: {reg['accion']}\n")
    if args.decidir_csv:
        df = pd.read_csv(args.decidir_csv)
        res = decisor.decidir_lote(df)
        salidas.mkdir(parents=True, exist_ok=True)
        ruta = salidas / "decisiones_csv.csv"
        res.to_csv(ruta, index=False)
        print(f"{len(res):,} transacciones de {args.decidir_csv} decididas:")
        print(res["nivel"].value_counts().reindex(["BAJO", "MEDIO", "ALTO"]).fillna(0).astype(int).to_string())
        print(f"Detalle en {ruta}")
    return 0


ACCION_CORTA = {"BAJO": "aprobada", "MEDIO": "aprobada + OTP al cliente", "ALTO": "retenida + analista humano"}
COLOR = {"BAJO": "\033[32m", "MEDIO": "\033[33m", "ALTO": "\033[31m", "fin": "\033[0m"}


def demo_en_vivo(oper: pd.DataFrame, scores: np.ndarray, sistema: SistemaAlertas, n: int, pausa: float) -> None:
    """Muestra transacciones llegando una a una, mezclando fraudes para que se vean en el video."""
    y = oper["es_fraude"].to_numpy()
    idx_fraude = np.where(y == 1)[0][: max(3, n // 6)]
    # Dos legítimas de nivel MEDIO para mostrar la verificación OTP en el video.
    nivel_medio = (y == 0) & (scores >= sistema.umbrales.medio) & (scores < sistema.umbrales.alto)
    idx_medio = np.where(nivel_medio)[0][:2]
    idx_normal = np.where((y == 0) & (scores < sistema.umbrales.medio))[0][: n - len(idx_fraude) - len(idx_medio)]
    orden = np.random.default_rng(7).permutation(np.concatenate([idx_fraude, idx_medio, idx_normal]))
    print(f"\nSimulando {len(orden)} transacciones en vivo (Ctrl+C para detener)...\n")
    print(f"{'tx_id':<10} {'cliente':>7} {'monto COP':>13} {'score':>6}  nivel   acción / motivos")
    try:
        for i in orden:
            fila = oper.iloc[i]
            reg = sistema.procesar(fila, scores[i])
            c = COLOR[reg["nivel"]]
            real = " [fraude real]" if fila.get("es_fraude", 0) == 1 else ""
            print(f"{reg['tx_id']:<10} {str(reg['cliente_id']):>7} {reg['monto']:>13,.0f} {reg['score']:>6.3f}  "
                  f"{c}{reg['nivel']:<6}{COLOR['fin']}  {ACCION_CORTA[reg['nivel']]}{real}")
            if reg["motivos"]:
                print(f"{'':<41}↳ {reg['motivos']}")
            if reg["propone_bloqueo_cuenta"]:
                print(f"{'':<41}↳ {COLOR['ALTO']}segunda alerta ALTA del cliente: se propone bloqueo preventivo (requiere analista){COLOR['fin']}")
            time.sleep(pausa)
    except KeyboardInterrupt:
        print("\nDemo interrumpida.")


if __name__ == "__main__":
    sys.exit(main())
