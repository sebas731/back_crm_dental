from django.conf import settings
from django.db import models

from shared.models import BaseModel


class Medico(BaseModel):
    """Profesional que atiende las citas."""

    # Vínculo opcional con un usuario del sistema (login).
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medico",
    )
    nombres = models.CharField(max_length=200)
    apellidos = models.CharField(max_length=200)
    especialidad = models.CharField(max_length=150, blank=True)
    colegiatura = models.CharField("N.º de colegiatura", max_length=50, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    correo = models.EmailField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Médico"
        verbose_name_plural = "Médicos"

    def __str__(self):
        return f"{self.nombres} {self.apellidos}".strip()
