from django.db import models

from shared.models import BaseModel

from .consultorio import Consultorio
from .medico import Medico
from .servicio import ServicioDental


class Cita(BaseModel):
    """Cita dental."""

    class Estado(models.TextChoices):
        PROGRAMADA = "PROGRAMADA", "Programada"
        CONFIRMADA = "CONFIRMADA", "Confirmada"
        EN_ATENCION = "EN_ATENCION", "En atención"
        ATENDIDA = "ATENDIDA", "Atendida"
        CANCELADA = "CANCELADA", "Cancelada"
        NO_ASISTIO = "NO_ASISTIO", "No asistió"

    paciente = models.ForeignKey(
        "pacientes.Paciente", on_delete=models.PROTECT, related_name="citas"
    )
    medico = models.ForeignKey(
        Medico, on_delete=models.PROTECT, related_name="citas"
    )
    servicio = models.ForeignKey(
        ServicioDental,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="citas",
    )
    # Consultorio/box donde se realiza la cita. Opcional y editable; muchas
    # citas pueden usar el mismo consultorio a lo largo del tiempo.
    consultorio = models.ForeignKey(
        Consultorio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="citas",
    )
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField(null=True, blank=True)
    estado = models.CharField(
        max_length=15, choices=Estado.choices, default=Estado.PROGRAMADA
    )
    motivo = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        ordering = ["-fecha", "-hora_inicio"]

    def __str__(self):
        return f"Cita {self.fecha} {self.hora_inicio} - {self.paciente}"
