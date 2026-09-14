from decimal import Decimal

from django.db import models

from shared.models import BaseModel

from ._common import CERO
from .venta import Venta


class Adicional(BaseModel):
    """Ítem adicional dinámico (material, insumo, laboratorio, etc.)."""

    venta = models.ForeignKey(
        Venta, on_delete=models.CASCADE, related_name="adicionales"
    )
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(
        max_length=100, blank=True, help_text="Ej: Material, Insumo, Laboratorio…"
    )
    valor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Adicional"
        verbose_name_plural = "Adicionales"

    @property
    def subtotal(self) -> Decimal:
        return (self.valor or CERO) * self.cantidad

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"
