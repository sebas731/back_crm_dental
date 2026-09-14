from django.db import models

from shared.models import BaseModel

from .historia_clinica_detalle import HistoriaClinicaDetalle
from .paciente import Paciente


class HistoriaClinica(BaseModel):
    """
    Historia clínica del paciente (modelo principal, liviano).

    El grueso de la ficha (antecedentes y revisiones) vive en
    `HistoriaClinicaDetalle`, referenciado por el FK `detalle`.
    """

    # PROTECT: borrar un paciente/cliente NO debe arrasar en silencio su
    # historia clínica (odontograma, antecedentes, documentos). Si tiene
    # historia, primero hay que eliminarla explícitamente.
    paciente = models.OneToOneField(
        Paciente, on_delete=models.PROTECT, related_name="historia_clinica"
    )
    numero = models.CharField(max_length=30, unique=True, blank=True)
    fecha_apertura = models.DateField(auto_now_add=True)
    observaciones = models.TextField(blank=True)

    # Detalle clínico propio de ESTA historia (1:1) — nunca compartido entre
    # pacientes. Puede quedar vacío hasta completar la ficha.
    detalle = models.OneToOneField(
        HistoriaClinicaDetalle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="historia",
    )

    class Meta:
        verbose_name = "Historia clínica"
        verbose_name_plural = "Historias clínicas"

    def __str__(self):
        return f"HC {self.numero or self.pk} - {self.paciente}"
