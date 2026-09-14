from django.conf import settings
from django.db import models

from shared.models import BaseModel


class NotaAgenda(BaseModel):
    """Anotación libre sobre una franja (día + hora) de la agenda."""

    fecha = models.DateField()
    hora = models.TimeField()
    texto = models.TextField()
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notas_agenda",
    )

    class Meta:
        verbose_name = "Nota de agenda"
        verbose_name_plural = "Notas de agenda"
        ordering = ["fecha", "hora", "created_at"]

    def __str__(self):
        return f"Nota {self.fecha} {self.hora}"
