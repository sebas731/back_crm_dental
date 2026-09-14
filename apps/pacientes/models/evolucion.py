from django.db import models

from shared.models import BaseModel

from .paciente import Paciente


class Evolucion(BaseModel):
    """
    Evolución clínica de un paciente: nota de seguimiento que registra un
    médico en una fecha (avance del tratamiento + observaciones).
    """

    paciente = models.ForeignKey(
        Paciente, on_delete=models.CASCADE, related_name="evoluciones"
    )
    medico = models.ForeignKey(
        "citas.Medico", on_delete=models.PROTECT, related_name="evoluciones"
    )
    # Cita médica de la que surge la evolución (opcional: puede registrarse
    # fuera de una cita). SET_NULL: borrar la cita no borra la evolución.
    cita = models.ForeignKey(
        "citas.Cita",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evoluciones",
    )
    evolucion = models.TextField("Evolución")
    observacion = models.TextField("Observación", blank=True)
    fecha_registro = models.DateTimeField("Fecha de registro", auto_now_add=True)

    class Meta:
        verbose_name = "Evolución"
        verbose_name_plural = "Evoluciones"
        ordering = ["-fecha_registro"]

    def __str__(self):
        return f"Evolución {self.fecha_registro:%Y-%m-%d} - {self.paciente}"
