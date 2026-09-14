from decimal import Decimal

from django.db import models

from shared.models import BaseModel

from ._common import CERO
from .venta import Venta


class Cuota(BaseModel):
    """
    Cuota del cronograma de pago de una venta. Al contado se genera 1 cuota.
    Editable: `fecha_limite` y su vínculo opcional a una `cita`.
    """

    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        PAGADO = "PAGADO", "Pagado"

    venta = models.ForeignKey(
        Venta, on_delete=models.CASCADE, related_name="cuotas"
    )
    numero = models.PositiveIntegerField(default=1)
    monto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_limite = models.DateField(null=True, blank=True)
    estado = models.CharField(
        max_length=10, choices=Estado.choices, default=Estado.PENDIENTE
    )
    # Vínculo opcional a la cita en la que se cobra/atiende esta cuota.
    cita = models.ForeignKey(
        "citas.Cita",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cuotas",
    )

    class Meta:
        verbose_name = "Cuota"
        verbose_name_plural = "Cuotas"
        ordering = ["venta", "numero"]
        constraints = [
            models.UniqueConstraint(
                fields=["venta", "numero"],
                name="cuota_numero_unico_por_venta",
            )
        ]

    @property
    def total_pagado(self) -> Decimal:
        return sum((p.monto for p in self.pagos.all()), CERO)

    @property
    def saldo(self) -> Decimal:
        return (self.monto or CERO) - self.total_pagado

    def actualizar_estado(self):
        # saldo <= 0 => PAGADO (incluye cuotas de monto 0, que antes quedaban
        # atascadas en PENDIENTE por la comprobación `self.monto`).
        nuevo = (
            self.Estado.PAGADO
            if self.saldo <= CERO
            else self.Estado.PENDIENTE
        )
        if nuevo != self.estado:
            self.estado = nuevo
            self.save(update_fields=["estado", "updated_at"])

    def __str__(self):
        return f"Cuota {self.numero}/{self.venta.cuotas.count()} - {self.venta}"
