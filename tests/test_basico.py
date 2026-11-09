# -*- coding: utf-8 -*-
"""Pruebas (desde la raíz del proyecto): python -m unittest discover -s tests -v"""
import tempfile
import unittest
from pathlib import Path

import numpy as np

from deteccion_fraude.alertas import SistemaAlertas, Umbrales
from deteccion_fraude.datos import COLUMNAS_MODELO, generar_transacciones
from deteccion_fraude.decision import DecisorFraude, transaccion_desde_texto
from deteccion_fraude.evaluacion import evaluar, umbral_por_presupuesto
from deteccion_fraude.modelo import DetectorAutoencoder, DetectorIsolationForest


class PruebasFraude(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = generar_transacciones(n=8_000, proporcion_fraude=0.01, semilla=1)

    def test_dataset_desbalanceado_y_reproducible(self):
        self.assertAlmostEqual(self.df.es_fraude.mean(), 0.01, places=3)
        otro = generar_transacciones(n=8_000, proporcion_fraude=0.01, semilla=1)
        self.assertTrue(self.df.equals(otro))

    def test_isolation_forest_detecta_mejor_que_el_azar(self):
        det = DetectorIsolationForest(contaminacion=0.01, n_arboles=100).entrenar(self.df[COLUMNAS_MODELO])
        s = det.puntuar(self.df[COLUMNAS_MODELO])
        r = evaluar("if", self.df.es_fraude.to_numpy(), s, umbral_por_presupuesto(s, 0.02))
        self.assertGreater(r.auc_roc, 0.9)
        self.assertGreater(r.recall, 0.5)

    def test_autoencoder_puntua_en_rango(self):
        det = DetectorAutoencoder(epocas=10).entrenar(self.df[COLUMNAS_MODELO])
        s = det.puntuar(self.df[COLUMNAS_MODELO])
        self.assertTrue(((s >= 0) & (s <= 1)).all())

    def test_sistema_de_alertas_nunca_bloquea_sin_revision(self):
        umb = Umbrales(medio=0.9, alto=0.97)
        sistema = SistemaAlertas(umb, COLUMNAS_MODELO, referencia=self.df[self.df.es_fraude == 0])
        fila = self.df.iloc[0]
        for score, nivel in [(0.1, "BAJO"), (0.92, "MEDIO"), (0.99, "ALTO")]:
            reg = sistema.procesar(fila, score)
            self.assertEqual(reg["nivel"], nivel)
        # Dos alertas altas del mismo cliente proponen bloqueo, pero siempre con revisión humana.
        self.assertTrue(reg["requiere_revision_humana"])
        reg2 = sistema.procesar(fila, 0.995)
        self.assertTrue(reg2["propone_bloqueo_cuenta"])
        self.assertTrue(reg2["requiere_revision_humana"])
        self.assertEqual(reg2["estado"], "PENDIENTE ANALISTA")

    def test_decisor_guarda_carga_y_decide(self):
        det = DetectorIsolationForest(contaminacion=0.01, n_arboles=100).entrenar(self.df[COLUMNAS_MODELO])
        s = det.puntuar(self.df[COLUMNAS_MODELO])
        umb = Umbrales.desde_presupuesto(s, 0.03, 0.01)
        decisor = DecisorFraude(det, umb, SistemaAlertas(umb, COLUMNAS_MODELO, referencia=self.df[self.df.es_fraude == 0]))
        with tempfile.TemporaryDirectory() as d:
            ruta = decisor.guardar(Path(d) / "m.pkl")
            cargado = DecisorFraude.cargar(ruta)
        fraude = cargado.decidir(transaccion_desde_texto("monto=5900000,hora=1,pin=4,dispositivo=1"))
        normal = cargado.decidir(transaccion_desde_texto("monto=45000,hora=13"))
        self.assertEqual(fraude["nivel"], "ALTO")
        self.assertTrue(fraude["requiere_revision_humana"])
        self.assertEqual(normal["nivel"], "BAJO")
        with self.assertRaises(ValueError):
            transaccion_desde_texto("variable_inexistente=1")


if __name__ == "__main__":
    unittest.main()
