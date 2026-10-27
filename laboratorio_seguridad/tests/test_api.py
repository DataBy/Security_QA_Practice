import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from servidor import ServidorLaboratorio
from src.lab import estado_inicial


class PruebasAPI(unittest.TestCase):
    def setUp(self):
        class Handler(ServidorLaboratorio):
            estado = estado_inicial()

            def log_message(self, *args):
                pass

        self.handler = Handler
        self.servidor = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.hilo = threading.Thread(target=self.servidor.serve_forever, daemon=True)
        self.hilo.start()
        self.base = f"http://127.0.0.1:{self.servidor.server_address[1]}"

    def tearDown(self):
        self.servidor.shutdown()
        self.servidor.server_close()
        self.hilo.join(timeout=2)

    def solicitar(self, metodo, ruta, token=None, datos=None, raw=None):
        headers = {}
        if token is not None:
            headers["Authorization"] = f"Bearer {token}"
        if datos is not None:
            headers["Content-Type"] = "application/json"
            raw = json.dumps(datos).encode("utf-8")
        peticion = Request(self.base + ruta, data=raw, headers=headers, method=metodo)
        try:
            respuesta = urlopen(peticion, timeout=3)
        except HTTPError as error:
            respuesta = error
        with respuesta:
            return respuesta.status, json.loads(respuesta.read().decode("utf-8")), respuesta.headers

    def test_api_01_estudiante_propio_con_encabezados_seguros(self):
        codigo, datos, headers = self.solicitar("GET", "/expedientes/101", "lab-ana")
        self.assertEqual(200, codigo)
        self.assertEqual(82, datos["nota"])
        self.assertEqual("no-store", headers["Cache-Control"])

    def test_api_02_docente_lectura_entre_sedes_denegada(self):
        codigo, datos, _ = self.solicitar("GET", "/expedientes/202", "lab-maria")
        self.assertEqual(403, codigo)
        self.assertNotIn("nota", datos)

    def test_api_03_nota_invalida_no_persiste(self):
        codigo, datos, _ = self.solicitar("POST", "/expedientes/101/nota", "lab-maria", {"nota": 101})
        self.assertEqual(400, codigo)
        self.assertNotIn("nota", datos)
        codigo, datos, _ = self.solicitar("GET", "/expedientes/101", "lab-ana")
        self.assertEqual((200, 82), (codigo, datos["nota"]))

    def test_api_04_revocacion_bloquea_lectura(self):
        self.assertEqual(200, self.solicitar("POST", "/sesiones/revocar", "lab-ana")[0])
        codigo, datos, _ = self.solicitar("GET", "/expedientes/101", "lab-ana")
        self.assertEqual(401, codigo)
        self.assertNotIn("nota", datos)

    def test_api_05_admin_no_modifica(self):
        codigo, datos, _ = self.solicitar("POST", "/expedientes/101/nota", "lab-admin", {"nota": 60})
        self.assertEqual(403, codigo)
        self.assertNotIn("nota", datos)
        self.assertEqual(82, self.handler.estado["expedientes"]["101"]["nota"])

    def test_api_06_json_invalido_y_booleano(self):
        codigo, datos, _ = self.solicitar("POST", "/expedientes/101/nota", "lab-maria", raw=b"{")
        self.assertEqual(400, codigo)
        codigo, datos, _ = self.solicitar("POST", "/expedientes/101/nota", "lab-maria", {"nota": True})
        self.assertEqual(400, codigo)
        self.assertEqual(82, self.handler.estado["expedientes"]["101"]["nota"])

    def test_api_07_sesion_expirada_no_lee(self):
        codigo, datos, _ = self.solicitar("GET", "/expedientes/101", "lab-vencida")
        self.assertEqual(401, codigo)
        self.assertNotIn("nota", datos)

    def test_api_08_sin_token_no_lee(self):
        codigo, datos, _ = self.solicitar("GET", "/expedientes/101")
        self.assertEqual(401, codigo)
        self.assertNotIn("nota", datos)


if __name__ == "__main__":
    unittest.main()
