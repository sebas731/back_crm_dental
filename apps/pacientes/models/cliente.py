from django.db import models

from shared.models import BaseModel


class Cliente(BaseModel):
    """Interesado en el servicio de atención (dato base que registran las empresas)."""

    nombre = models.CharField(max_length=150)
    apellido = models.CharField(max_length=150)
    segundo_apellido = models.CharField(max_length=150, blank=True)
    correo = models.EmailField(blank=True)
    numero = models.CharField("Número de contacto", max_length=30, blank=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return f"{self.nombre} {self.apellido}".strip()
