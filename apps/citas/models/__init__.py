"""
Modelos de la agenda dental, separados en un archivo por modelo. El paquete
re-exporta todo, así el resto del proyecto sigue importando con
`from apps.citas.models import X`.

- Medico: profesional que atiende.
- ServicioDental: catálogo de servicios/procedimientos (jerárquico).
- HorarioAtencion: franjas horarias de atención por médico (disponibilidad).
- Cita: cita dental (con estados).
- AtencionCita: detalle de la cita al cerrarse (atendido / faltó / no pagó).
- NotaAgenda: anotación libre sobre una franja de la agenda.
"""

from .atencion import AtencionCita
from .cita import Cita
from .horario import HorarioAtencion
from .medico import Medico
from .nota import NotaAgenda
from .servicio import ServicioDental

__all__ = [
    "Medico",
    "ServicioDental",
    "HorarioAtencion",
    "Cita",
    "AtencionCita",
    "NotaAgenda",
]
