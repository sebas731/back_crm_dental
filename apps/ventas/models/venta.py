from decimal import Decimal

from django.conf import settings
from django.db import models

from shared.models import BaseModel

from ._common import CERO, generar_numero_venta


class Venta(BaseModel):
    class TipoPago(models.TextChoices):
        CONTADO = "CONTADO", "Contado"
        CUOTAS = "CUOTAS", "Cuotas"

    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        PAGADO = "PAGADO", "Pagado"
        ANULADO = "ANULADO", "Anulado"

    numero = models.CharField(max_length=30, unique=True, blank=True)
    paciente = models.ForeignKey(
        "pacientes.Paciente", on_delete=models.PROTECT, related_name="ventas"
    )
    # Venta generada automáticamente al agendar una cita (1:1 opcional).
    cita = models.OneToOneField(
        "citas.Cita",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="venta",
    )
    tipo_pago = models.CharField(
        max_length=10, choices=TipoPago.choices, default=TipoPago.CONTADO
    )
    estado = models.CharField(
        max_length=10, choices=Estado.choices, default=Estado.PENDIENTE
    )
    # Total congelado de la venta (monto acordado con el paciente).
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    observaciones = models.TextField(blank=True)
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ventas_registradas",
    )

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Venta {self.numero or self.pk} - {self.paciente}"

    def save(self, *args, **kwargs):
        # Garantiza un número único aunque no se envíe (evita vacío/duplicado).
        if not self.numero:
            self.numero = generar_numero_venta()
        super().save(*args, **kwargs)

    # --- Cálculos (derivados de las líneas) ---
    @property
    def subtotal_servicios(self) -> Decimal:
        return sum((i.subtotal for i in self.servicios.all()), CERO)

    @property
    def subtotal_adicionales(self) -> Decimal:
        return sum((a.subtotal for a in self.adicionales.all()), CERO)

    @property
    def total_descuentos(self) -> Decimal:
        base = self.subtotal_servicios + self.subtotal_adicionales
        return sum((d.monto_aplicado(base) for d in self.descuentos.all()), CERO)

    @property
    def total_calculado(self) -> Decimal:
        """Total sugerido a partir de las líneas (para congelar en `total`)."""
        return self.subtotal_servicios + self.subtotal_adicionales - self.total_descuentos

    @property
    def total_pagado(self) -> Decimal:
        return sum((c.total_pagado for c in self.cuotas.all()), CERO)

    @property
    def saldo(self) -> Decimal:
        return (self.total or CERO) - self.total_pagado

    def recalcular_total(self):
        """Congela `total` a partir de las líneas (servicios/adicionales/desc.)."""
        self.total = self.total_calculado
        self.save(update_fields=["total", "updated_at"])

    def actualizar_estado(self):
        """Marca PAGADO cuando no queda saldo (no toca ventas anuladas)."""
        if self.estado == self.Estado.ANULADO:
            return
        # Nota: se compara el saldo directamente. Antes se exigía `self.total`
        # (verdad-ez), lo que dejaba atascada en PENDIENTE cualquier venta de
        # total 0 (saldo 0). Ahora saldo <= 0 => PAGADO.
        nuevo = (
            self.Estado.PAGADO
            if self.saldo <= CERO
            else self.Estado.PENDIENTE
        )
        if nuevo != self.estado:
            self.estado = nuevo
            self.save(update_fields=["estado", "updated_at"])

    # --- Inmutabilidad (congelado de documento financiero) ---
    @property
    def tiene_pagos_validados(self) -> bool:
        """¿Algún pago de la venta ya fue validado?"""
        return any(
            p.validado for c in self.cuotas.all() for p in c.pagos.all()
        )

    @property
    def editable(self) -> bool:
        """
        Una venta se congela (no se editan sus factores: servicios,
        adicionales, descuentos) cuando está anulada o ya tiene algún pago
        validado. Para corregirla se duplica y se anula la original.
        """
        return (
            self.estado != self.Estado.ANULADO
            and not self.tiene_pagos_validados
        )

    def anular(self, motivo: str = ""):
        """Anula la venta (p. ej. para devoluciones). Conserva su historial."""
        self.estado = self.Estado.ANULADO
        if motivo:
            sep = "\n" if self.observaciones else ""
            self.observaciones = f"{self.observaciones}{sep}[ANULADA] {motivo}"
        self.save(update_fields=["estado", "observaciones", "updated_at"])
        return self
