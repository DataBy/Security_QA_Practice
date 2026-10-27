# Laboratorio de Pruebas de Seguridad de Software

Proyecto académico local de **datos exclusivamente sintéticos**. No es una autenticación para producción. El servidor escucha únicamente en `127.0.0.1`.

## Entorno y ejecución

- Python 3.10+; biblioteca estándar, sin `pip install`.
- Linux/macOS: `python3`; Windows: `py -3` o `python`.
- Desde la raíz `laboratorio_seguridad/` ejecutar, exactamente:

```bash
python3 -m unittest discover -s tests -v
python3 servidor.py
```

En otra terminal:

```bash
curl -i -H 'Authorization: Bearer lab-ana' http://127.0.0.1:8765/expedientes/101
curl -i -H 'Authorization: Bearer lab-maria' http://127.0.0.1:8765/expedientes/202
curl -i -X POST -H 'Authorization: Bearer lab-maria' -H 'Content-Type: application/json' -d '{"nota":101}' http://127.0.0.1:8765/expedientes/101/nota
```

Para detener: `Ctrl+C`. Para **restablecer todos los datos y sesiones**: detener y reiniciar `servidor.py`. Cada prueba automatizada crea su propio estado. La suite API usa un puerto local efímero para evitar conflictos.

## Usuarios simulados

| Token didáctico | Usuario | Rol | Sede |
| --- | --- | --- | --- |
| `lab-ana` | Ana | estudiante | Central |
| `lab-luis` | Luis | estudiante | Pacífico |
| `lab-maria` | María | docente | Central |
| `lab-pedro` | Pedro | docente | Pacífico |
| `lab-admin` | Admin | administrador | ambas |
| `lab-vencida` | Ana | sesión expirada | Central |

Las lecturas permitidas devuelven `200`; las prohibidas por rol/sede `403`; las sesiones inválidas `401`; las notas inválidas `400`. Las respuestas de rechazo no incluyen notas. Un estudiante lee exclusivamente su expediente; un docente lee y modifica exclusivamente su sede; el administrador lee ambas, sin modificar notas.

## Pruebas y evidencia

- `tests/test_laboratorio.py`: 12 casos TC-01 a TC-12 y pruebas unitarias adicionales.
- `tests/test_api.py`: pruebas de integración HTTP real en localhost.
- `../evidencias/`: dos ejecuciones limpias, TDD rojo/verde/refactor, HTTP manual y comprobación estática.
- `../matriz_trazabilidad.csv`: requisitos, riesgos, pasos y resultados por caso.
- `../hallazgos.csv`: defectos y sus correcciones.
- `../informe_seguridad.pdf`: informe y dictamen.

No se prueba ninguna red, web ni servicio ajeno. Los tokens aquí son valores ficticios deliberadamente públicos. Los registros de auditoría no almacenan tokens ni calificaciones. El modelo en memoria no tiene persistencia real ni cifrado, control de concurrencia transaccional o protección de producción.

## Ejecución independiente

1. Extraer ZIP; abrir terminal en `laboratorio_seguridad/`.
2. Confirmar `python3 --version` (3.10+) y lanzar `python3 -m unittest discover -s tests -v`.
3. Confirmar todos los casos aprobados; repetir en nueva invocación.
4. Ejecutar `python3 servidor.py` y repetir los `curl` anteriores.
5. Parar servidor y reiniciar para restablecer los datos.

La inspección por otro integrante y la repetición independiente del README deben ser realizadas y firmadas por una persona real; no se atribuyen falsamente a un compañero.
