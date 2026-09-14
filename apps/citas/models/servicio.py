from django.db import models

from shared.models import BaseModel


class ServicioDental(BaseModel):
    """
    Servicio o procedimiento dental. Soporta jerarquía: una categoría
    (``padre`` nulo) agrupa subservicios que la referencian por ``padre``.
    """

    padre = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subservicios",
    )
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duracion_minutos = models.PositiveIntegerField(
        "Duración estimada (min)", default=30
    )
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Servicio dental"
        verbose_name_plural = "Servicios dentales"
        ordering = ["nombre"]

    @property
    def es_categoria(self) -> bool:
        return self.padre_id is None

    def __str__(self):
        return self.nombre
