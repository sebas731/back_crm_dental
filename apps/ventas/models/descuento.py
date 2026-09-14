from decimal import Decimal

from django.db import models

from shared.models import BaseModel

from ._common import CERO
from .venta import Venta


class Descuento(BaseModel):
    class Tipo(models.TextChoices):
        MONTO = "MONTO", "Monto fijo"
        PORCENTAJE = "PORCENTAJE", "Porcentaje"

    venta = models.ForeignKey(
        Venta, on_delete=models.CASCADE, related_name="descuentos"
    )
    descripcion = models.CharField(max_length=200, blank=True)
    tipo = models.CharField(max_length=10, choices=Tipo.choices, default=Tipo.MONTO)
    valor = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Descuento"
        verbose_name_plural = "Descuentos"

    def monto_aplicado(self, base: Decimal) -> Decimal:
        if self.tipo == self.Tipo.PORCENTAJE:
            return (base or CERO) * (self.valor or CERO) / Decimal("100")
        return self.valor or CERO

    def __str__(self):
        return f"Descuento {self.get_tipo_display()} {self.valor}"
