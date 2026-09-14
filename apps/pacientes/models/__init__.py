"""
Modelos de dominio de la app `pacientes`, separados en un archivo por modelo
(estilo clean architecture). Este paquete re-exporta todos los modelos, de modo
que el resto del proyecto sigue importando con `from apps.pacientes.models import X`.

Relaciones:
- Paciente HEREDA de Cliente (herencia multi-tabla / MTI): un Paciente ES un
  Cliente. Cliente es el "interesado" del servicio; el Paciente es la
  especialización con todos los datos clínicos.
- Un Paciente tiene N Acompanante (FK).
- Un Paciente tiene una HistoriaClinica (OneToOne, PROTECT).
- HistoriaClinica tiene un HistoriaClinicaDetalle (OneToOne), N documentos,
  N odontogramas y unos AntecedentesPersonales (1:1).
"""

from .acompanante import Acompanante
from .antecedentes import AntecedentesPersonales
from .cliente import Cliente
from .documento import DocumentoHistoriaClinica
from .historia_clinica import HistoriaClinica
from .historia_clinica_detalle import HistoriaClinicaDetalle
from .odontograma import Odontograma
from .paciente import Paciente

__all__ = [
    "Cliente",
    "Paciente",
    "Acompanante",
    "HistoriaClinicaDetalle",
    "HistoriaClinica",
    "DocumentoHistoriaClinica",
    "Odontograma",
    "AntecedentesPersonales",
]
