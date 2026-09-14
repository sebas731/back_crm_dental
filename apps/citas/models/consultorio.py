from django.db import models

from shared.models import BaseModel


class Consultorio(BaseModel):
    """
    Consultorio / box de atención de la clínica (Ej: "Consultorio Principal",
    "Box de Cirugía", "Sala 2"). Por ahora solo guarda datos maestros; más
    adelante se podrá vincular a las citas para gestionar disponibilidad.
    """

    nombre = models.CharField(max_length=100)
    # Normalmente 1 por privacidad; permite más en salas comunales/simulación.
    capacidad_sillones = models.PositiveIntegerField(
        "Capacidad de sillones", default=1
    )
    ubicacion_interna = models.CharField(
        "Ubicación interna",
        max_length=150,
        blank=True,
        help_text='Ej: "Piso 2, Ala Izquierda", "Al fondo junto a recepción"',
    )
    equipamiento_especial = models.TextField(
        blank=True,
        help_text='Ej: "Máquina de Rayos X integrada, cámara intraoral"',
    )
    # Permite deshabilitarlo temporalmente (p. ej. si entra en mantenimiento).
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Consultorio"
        verbose_name_plural = "Consultorios"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
