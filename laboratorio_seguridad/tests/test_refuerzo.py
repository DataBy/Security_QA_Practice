import unittest
from src.lab import actualizar_nota, estado_inicial, leer_expediente, revocar_sesion


class RefuerzoSeguridad(unittest.TestCase):
    def setUp(self):
        self.estado = estado_inicial()

    def test_01_entero_enorme_rechazado_sin_excepcion(self):
        codigo, datos = actualizar_nota(self.estado, "lab-maria", "101", 10 ** 400)
        self.assertEqual(codigo, 400)
        self.assertNotIn("nota", datos)
        self.assertEqual(self.estado["expedientes"]["101"]["nota"], 82)

    def test_02_infinito_negativo_rechazado(self):
        codigo, datos = actualizar_nota(self.estado, "lab-maria", "101", float("-inf"))
        self.assertEqual(codigo, 400)
        self.assertNotIn("nota", datos)
        self.assertEqual(self.estado["expedientes"]["101"]["nota"], 82)

    def test_03_decimal_en_rango_aceptado(self):
        codigo, datos = actualizar_nota(self.estado, "lab-maria", "101", 99.5)
        self.assertEqual((codigo, datos["nota"]), (200, 99.5))

    def test_04_luis_solo_consulta_expediente_propio(self):
        self.assertEqual(leer_expediente(self.estado, "lab-luis", "202")[0], 200)
        codigo, datos = leer_expediente(self.estado, "lab-luis", "101")
        self.assertEqual(codigo, 403)
        self.assertNotIn("nota", datos)

    def test_05_pedro_actualiza_solo_pacifico(self):
        self.assertEqual(actualizar_nota(self.estado, "lab-pedro", "202", 76)[0], 200)
        codigo, datos = actualizar_nota(self.estado, "lab-pedro", "101", 55)
        self.assertEqual(codigo, 403)
        self.assertNotIn("nota", datos)
        self.assertEqual(self.estado["expedientes"]["101"]["nota"], 82)

    def test_06_sesion_vencida_no_se_puede_revocar(self):
        codigo, datos = revocar_sesion(self.estado, "lab-vencida")
        self.assertEqual(codigo, 401)
        self.assertNotIn("nota", datos)

    def test_07_revocacion_no_permite_reutilizacion(self):
        self.assertEqual(revocar_sesion(self.estado, "lab-ana")[0], 200)
        self.assertEqual(revocar_sesion(self.estado, "lab-ana")[0], 401)
        self.assertEqual(leer_expediente(self.estado, "lab-ana", "101")[0], 401)

    def test_08_auditoria_de_fallo_no_incluye_token(self):
        leer_expediente(self.estado, "lab-desconocido", "101")
        actualizar_nota(self.estado, "lab-maria", "202", 75)
        auditoria = str(self.estado["auditoria"])
        self.assertNotIn("lab-", auditoria)
        self.assertNotIn("nota", auditoria)
        self.assertTrue(all("resultado" in evento for evento in self.estado["auditoria"]))


if __name__ == "__main__":
    unittest.main()
