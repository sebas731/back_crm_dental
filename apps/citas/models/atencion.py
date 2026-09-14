from django.db import models

from shared.models import BaseModel

from .cita import Cita
from .medico import Medico


class AtencionCita(BaseModel):
    """
    Detalle de la cita al ser atendida. Se crea cuando la cita se cierra
    (atendido / faltó / no pagó).
    """

    class Estado(models.TextChoices):
        ATENDIDO = "ATENDIDO", "Atendido"
        FALTO = "FALTO", "Faltó"
        NO_PAGO = "NO_PAGO", "No pagó (no se atendió)"

    cita = models.OneToOneField(
        Cita, on_delete=models.CASCADE, related_name="atencion"
    )
    fecha_cita = models.DateField()
    estado = models.CharField(
        max_length=10, choices=Estado.choices, default=Estado.ATENDIDO
    )
    descripcion = models.TextField("Descripción de la cita", blank=True)
    evolucion = models.TextField("Evolución del tratamiento", blank=True)
    medico_atendio = models.ForeignKey(
        Medico, on_delete=models.PROTECT, related_name="atenciones"
    )
    # Firma como texto por ahora; luego se reemplaza por firma digital.
    firma = models.TextField(blank=True)

    class Meta:
        verbose_name = "Atención de cita"
        verbose_name_plural = "Atenciones de cita"
        ordering = ["-fecha_cita"]

    def __str__(self):
        return f"Atención {self.get_estado_display()} - {self.cita}"
