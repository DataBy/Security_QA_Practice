"""API didáctica HTTP accesible exclusivamente desde 127.0.0.1."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
from src.lab import actualizar_nota, estado_inicial, leer_expediente, revocar_sesion


class ServidorLaboratorio(BaseHTTPRequestHandler):
    estado = estado_inicial()

    def _token(self):
        autorizacion = self.headers.get("Authorization", "")
        return autorizacion[7:] if autorizacion.startswith("Bearer ") else ""

    def _salida(self, codigo, datos):
        cuerpo = json.dumps(datos, ensure_ascii=False, allow_nan=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_GET(self):
        partes = urlsplit(self.path).path.strip("/").split("/")
        if partes == ["health"]:
            return self._salida(200, {"estado": "laboratorio"})
        if len(partes) == 2 and partes[0] == "expedientes":
            return self._salida(*leer_expediente(self.estado, self._token(), partes[1]))
        return self._salida(404, {"error": "Ruta inexistente"})

    def do_POST(self):
        partes = urlsplit(self.path).path.strip("/").split("/")
        if partes == ["sesiones", "revocar"]:
            return self._salida(*revocar_sesion(self.estado, self._token()))
        if len(partes) == 3 and partes[0] == "expedientes" and partes[2] == "nota":
            try:
                cantidad = int(self.headers.get("Content-Length", "0"))
                if cantidad < 0:
                    return self._salida(400, {"error": "Longitud inválida"})
                if cantidad > 1024:
                    return self._salida(413, {"error": "Solicitud demasiado grande"})
                datos = json.loads(self.rfile.read(cantidad).decode("utf-8"), parse_constant=lambda _: None)
                if not isinstance(datos, dict):
                    return self._salida(400, {"error": "Objeto JSON esperado"})
            except (ValueError, UnicodeError):
                return self._salida(400, {"error": "JSON inválido"})
            return self._salida(*actualizar_nota(self.estado, self._token(), partes[1], datos.get("nota")))
        return self._salida(404, {"error": "Ruta inexistente"})

    def log_message(self, formato, *argumentos):
        print("[LAB] " + formato % argumentos)


if __name__ == "__main__":
    servidor = ThreadingHTTPServer(("127.0.0.1", 8765), ServidorLaboratorio)
    print("Laboratorio: http://127.0.0.1:8765")
    servidor.serve_forever()
