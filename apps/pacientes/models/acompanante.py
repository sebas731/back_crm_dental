from django.db import models

from shared.models import BaseModel

from .paciente import Paciente


class Acompanante(BaseModel):
    """Acompañante de un Paciente (dato extra)."""

    class Parentesco(models.TextChoices):
        PADRE = "PADRE", "Padre"
        MADRE = "MADRE", "Madre"
        HERMANO = "HERMANO", "Hermano/a"
        ABUELO = "ABUELO", "Abuelo/a"
        TIO = "TIO", "Tío/a"
        TUTOR = "TUTOR", "Tutor legal"
        OTRO = "OTRO", "Otro"

    paciente = models.ForeignKey(
        Paciente, on_delete=models.CASCADE, related_name="acompanantes"
    )
    nombre = models.CharField(max_length=150)
    apellido_paterno = models.CharField(max_length=150)
    apellido_materno = models.CharField(max_length=150, blank=True)
    dni = models.CharField(max_length=20)
    parentesco = models.CharField(max_length=10, choices=Parentesco.choices)
    telefono = models.CharField(max_length=30, blank=True)

    class Meta:
        verbose_name = "Acompañante"
        verbose_name_plural = "Acompañantes"

    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno} ({self.get_parentesco_display()})"
