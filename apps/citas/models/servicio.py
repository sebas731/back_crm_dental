from django.db import models

from shared.models import BaseModel


class ServicioDental(BaseModel):
    """
    Servicio o procedimiento dental. Soporta jerarquía: una categoría
    (``padre`` nulo) agrupa subservicios que la referencian por ``padre``.
    """

    class Moneda(models.TextChoices):
        PEN = "PEN", "S/ (Soles)"
        USD = "USD", "US$ (Dólares)"

    padre = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subservicios",
    )
    # Código/SKU opcional que trae el cliente en su Excel (no es el id interno).
    codigo = models.CharField("Código de producto", max_length=50, blank=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    moneda = models.CharField(
        max_length=3, choices=Moneda.choices, default=Moneda.PEN
    )
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Insumos que consume/necesita este servicio (batas, materiales, etc.).
    insumos = models.ManyToManyField(
        "Insumo", related_name="servicios", blank=True
    )
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
