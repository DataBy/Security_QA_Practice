# Entrega - Seguridad de software (ISW-622)

**Autor registrado:** Byron Bolaños Zamora. **Fecha:** 27/10/2026.

- `informe_seguridad.pdf`: informe técnico original de tres páginas.
- `informe_resumen_1_pagina.pdf`: resumen actualizado de una página, sin colores.
- `laboratorio_seguridad/`: código del laboratorio y 34 pruebas automatizadas, ejecutables con Python 3.10+.
- `evidencias/`: fases rojo, verde, refactor; dos regresiones y solicitudes HTTP manuales.
- `matriz_trazabilidad.csv`: definición de 12 casos (3 positivos, 6 negativos y 3 de frontera), más prueba adicional de auditoría.
- `hallazgos.csv`: hallazgos y tratamientos.
- `acta_inspeccion.md`: autorrevisión documentada y espacios sin falsear para inspección de otro integrante y repetición del README.

**Reproducir:** `cd laboratorio_seguridad && python3 -m unittest discover -s tests -v`.

**Limitaciones administrativas pendientes:** un segundo integrante real, inspección cruzada por alguien distinto del autor, reproducción independiente por otro integrante y un segundo día con commits de cada participante. Los commits hechos hoy no se retrofechan. Nadie puede garantizar una calificación determinada.

**Verificación CI:** 34 pruebas correctas en Python 3.10, 3.12 y 3.13. https://github.com/DataBy/Security_QA_Practice/actions/runs/40580311049
