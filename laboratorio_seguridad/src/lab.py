"""Motor didáctico de expedientes y sesiones sintéticas. No apto para producción."""

import math

USUARIOS = {
    "ana": {"id": "ana", "rol": "estudiante", "sede": "Central"},
    "luis": {"id": "luis", "rol": "estudiante", "sede": "Pacifico"},
    "maria": {"id": "maria", "rol": "docente", "sede": "Central"},
    "pedro": {"id": "pedro", "rol": "docente", "sede": "Pacifico"},
    "admin": {"id": "admin", "rol": "administrador", "sede": None},
}


def estado_inicial():
    return {
        "expedientes": {
            "101": {"id": "101", "estudiante": "ana", "sede": "Central", "nota": 82},
            "202": {"id": "202", "estudiante": "luis", "sede": "Pacifico", "nota": 91},
        },
        "sesiones": {
            f"lab-{identificador}": {"usuario": identificador, "revocada": False, "expirada": False}
            for identificador in USUARIOS
        } | {"lab-vencida": {"usuario": "ana", "revocada": False, "expirada": True}},
        "auditoria": [],
    }


def _sesion_activa(sesion):
    return bool(sesion) and not sesion["revocada"] and not sesion["expirada"]


def autenticar(estado, token):
    sesion = estado["sesiones"].get(token) if isinstance(token, str) else None
    return USUARIOS.get(sesion["usuario"]) if _sesion_activa(sesion) else None


def _puede_leer(usuario, expediente):
    if usuario["rol"] == "estudiante":
        return expediente["estudiante"] == usuario["id"]
    if usuario["rol"] == "docente":
        return expediente["sede"] == usuario["sede"]
    return usuario["rol"] == "administrador"


def _puede_cambiar(usuario, expediente):
    return usuario["rol"] == "docente" and expediente["sede"] == usuario["sede"]


def _nota_valida(nota):
    return type(nota) in (int, float) and math.isfinite(nota) and 0 <= nota <= 100


def _auditar(estado, usuario, accion, recurso, resultado):
    estado["auditoria"].append({
        "actor": usuario["id"] if usuario else "desconocido",
        "accion": accion,
        "recurso": str(recurso),
        "resultado": resultado,
    })


def leer_expediente(estado, token, expediente_id):
    usuario = autenticar(estado, token)
    if usuario is None:
        _auditar(estado, None, "lectura", expediente_id, "rechazado")
        return 401, {"error": "Sesión inválida o vencida"}
    expediente = estado["expedientes"].get(expediente_id)
    if expediente is None:
        _auditar(estado, usuario, "lectura", expediente_id, "no_encontrado")
        return 404, {"error": "Recurso no disponible"}
    if not _puede_leer(usuario, expediente):
        _auditar(estado, usuario, "lectura", expediente_id, "rechazado")
        return 403, {"error": "Acceso denegado"}
    _auditar(estado, usuario, "lectura", expediente_id, "permitido")
    return 200, dict(expediente)


def actualizar_nota(estado, token, expediente_id, nota):
    usuario = autenticar(estado, token)
    if usuario is None:
        _auditar(estado, None, "actualizacion", expediente_id, "rechazado")
        return 401, {"error": "Sesión inválida o vencida"}
    expediente = estado["expedientes"].get(expediente_id)
    if expediente is None:
        _auditar(estado, usuario, "actualizacion", expediente_id, "no_encontrado")
        return 404, {"error": "Recurso no disponible"}
    if not _puede_cambiar(usuario, expediente):
        _auditar(estado, usuario, "actualizacion", expediente_id, "rechazado")
        return 403, {"error": "Acceso denegado"}
    if not _nota_valida(nota):
        _auditar(estado, usuario, "actualizacion", expediente_id, "invalido")
        return 400, {"error": "Nota inválida: use un número entre 0 y 100"}
    expediente["nota"] = nota
    _auditar(estado, usuario, "actualizacion", expediente_id, "permitido")
    return 200, dict(expediente)


def revocar_sesion(estado, token):
    usuario = autenticar(estado, token)
    if usuario is None:
        _auditar(estado, None, "revocacion", "sesion", "rechazado")
        return 401, {"error": "Sesión inválida o vencida"}
    estado["sesiones"][token]["revocada"] = True
    _auditar(estado, usuario, "revocacion", "sesion", "permitido")
    return 200, {"mensaje": "Sesión revocada"}
