import unittest
from src.lab import actualizar_nota, estado_inicial, leer_expediente, revocar_sesion


class CasosDeSeguridad(unittest.TestCase):
    def setUp(self):
        self.estado = estado_inicial()

    def test_TC01_estudiante_lee_su_expediente(self):
        codigo, datos = leer_expediente(self.estado, "lab-ana", "101")
        self.assertEqual((200, "ana", 82), (codigo, datos.get("estudiante"), datos.get("nota")))

    def test_TC02_estudiante_no_lee_expediente_ajeno_ni_nota(self):
        antes = self.estado["expedientes"]["202"].copy()
        codigo, datos = leer_expediente(self.estado, "lab-ana", "202")
        self.assertEqual(403, codigo)
        self.assertNotIn("nota", datos)
        self.assertEqual(antes, self.estado["expedientes"]["202"])

    def test_TC03_docente_no_modifica_nota_en_otra_sede(self):
        antes = self.estado["expedientes"]["202"].copy()
        codigo, datos = actualizar_nota(self.estado, "lab-maria", "202", 15)
        self.assertEqual(403, codigo)
        self.assertNotIn("nota", datos)
        self.assertEqual(antes, self.estado["expedientes"]["202"])

    def test_TC04_sesion_revocada_no_lee(self):
        self.assertEqual(200, revocar_sesion(self.estado, "lab-ana")[0])
        codigo, datos = leer_expediente(self.estado, "lab-ana", "101")
        self.assertEqual(401, codigo)
        self.assertNotIn("nota", datos)

    def test_TC05_nota_menos_uno_no_se_guarda(self):
        anterior = self.estado["expedientes"]["101"]["nota"]
        codigo, datos = actualizar_nota(self.estado, "lab-maria", "101", -1)
        self.assertEqual(400, codigo)
        self.assertNotIn("nota", datos)
        self.assertEqual(anterior, self.estado["expedientes"]["101"]["nota"])

    def test_TC06_docente_actualiza_su_sede(self):
        codigo, datos = actualizar_nota(self.estado, "lab-maria", "101", 85)
        self.assertEqual((200, 85), (codigo, datos.get("nota")))
        self.assertEqual(85, self.estado["expedientes"]["101"]["nota"])

    def test_TC07_administrador_lee_ambas_sedes(self):
        for expediente_id in ("101", "202"):
            with self.subTest(expediente=expediente_id):
                codigo, datos = leer_expediente(self.estado, "lab-admin", expediente_id)
                self.assertEqual(200, codigo)
                self.assertEqual(expediente_id, datos["id"])

    def test_TC08_sesion_expirada_no_lee(self):
        codigo, datos = leer_expediente(self.estado, "lab-vencida", "101")
        self.assertEqual(401, codigo)
        self.assertNotIn("nota", datos)

    def test_TC09_administrador_no_modifica_nota(self):
        anterior = self.estado["expedientes"]["101"]["nota"]
        codigo, datos = actualizar_nota(self.estado, "lab-admin", "101", 99)
        self.assertEqual(403, codigo)
        self.assertNotIn("nota", datos)
        self.assertEqual(anterior, self.estado["expedientes"]["101"]["nota"])

    def test_TC10_sin_token_no_lee(self):
        codigo, datos = leer_expediente(self.estado, "", "101")
        self.assertEqual(401, codigo)
        self.assertNotIn("nota", datos)

    def test_TC11_nota_cien_es_valida(self):
        codigo, datos = actualizar_nota(self.estado, "lab-maria", "101", 100)
        self.assertEqual((200, 100), (codigo, datos.get("nota")))
        self.assertEqual(100, self.estado["expedientes"]["101"]["nota"])

    def test_TC12_nota_ciento_uno_no_se_guarda(self):
        anterior = self.estado["expedientes"]["101"]["nota"]
        codigo, datos = actualizar_nota(self.estado, "lab-maria", "101", 101)
        self.assertEqual(400, codigo)
        self.assertNotIn("nota", datos)
        self.assertEqual(anterior, self.estado["expedientes"]["101"]["nota"])

    def test_extra_auditoria_sin_token_ni_nota(self):
        leer_expediente(self.estado, "lab-ana", "202")
        actualizar_nota(self.estado, "lab-maria", "101", 90)
        auditoria = repr(self.estado["auditoria"])
        self.assertNotIn("lab-", auditoria)
        self.assertNotIn("nota", auditoria)
        self.assertEqual("rechazado", self.estado["auditoria"][0]["resultado"])
        self.assertEqual("permitido", self.estado["auditoria"][1]["resultado"])

    def test_extra_docente_no_lee_otra_sede(self):
        codigo, datos = leer_expediente(self.estado, "lab-maria", "202")
        self.assertEqual(403, codigo)
        self.assertNotIn("nota", datos)

    def test_extra_estudiante_no_modifica_nota(self):
        codigo, datos = actualizar_nota(self.estado, "lab-ana", "101", 77)
        self.assertEqual(403, codigo)
        self.assertNotIn("nota", datos)
        self.assertEqual(82, self.estado["expedientes"]["101"]["nota"])

    def test_extra_nota_cero_es_valida(self):
        codigo, datos = actualizar_nota(self.estado, "lab-pedro", "202", 0)
        self.assertEqual((200, 0), (codigo, datos.get("nota")))

    def test_extra_bool_nan_inf_cadena_rechazados(self):
        for valor in (True, float("nan"), float("inf"), "85", None):
            with self.subTest(valor=repr(valor)):
                codigo, _ = actualizar_nota(self.estado, "lab-maria", "101", valor)
                self.assertEqual(400, codigo)
                self.assertEqual(82, self.estado["expedientes"]["101"]["nota"])

    def test_extra_sesion_revocada_no_modifica_nota(self):
        revocar_sesion(self.estado, "lab-maria")
        codigo, datos = actualizar_nota(self.estado, "lab-maria", "101", 60)
        self.assertEqual(401, codigo)
        self.assertNotIn("nota", datos)
        self.assertEqual(82, self.estado["expedientes"]["101"]["nota"])


if __name__ == "__main__":
    unittest.main()
