from decimal import Decimal

from django.db import models

from shared.models import BaseModel

from ._common import CERO
from .venta import Venta


class VentaServicio(BaseModel):
    """Servicio aplicado a una venta (con su precio congelado al momento)."""

    venta = models.ForeignKey(
        Venta, on_delete=models.CASCADE, related_name="servicios"
    )
    servicio = models.ForeignKey(
        "citas.ServicioDental", on_delete=models.PROTECT, related_name="ventas"
    )
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )

    class Meta:
        verbose_name = "Servicio de venta"
        verbose_name_plural = "Servicios de venta"

    @property
    def subtotal(self) -> Decimal:
        return (self.precio_unitario or CERO) * self.cantidad

    def __str__(self):
        return f"{self.servicio} x{self.cantidad}"
