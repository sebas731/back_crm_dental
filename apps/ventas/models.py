"""
Venta de servicios dentales y su cobranza.

Jerarquía:
    Venta (nota de venta / cuenta del paciente)
      ├── VentaServicio  (1:N)  servicios aplicados (precio congelado)
      ├── Descuento      (1:N)  descuentos por monto o porcentaje
      ├── Adicional      (1:N)  materiales / insumos / extras (dinámico)
      └── Cuota          (1:N)  cronograma de pago (contado => 1 cuota)
             └── Pago    (1:N)  pagos que solventan la cuota

Reglas:
- La venta es como una "nota": una vez creada, lo editable es su `estado`
  (los montos/servicios no deberían modificarse; se recalculan/congelan).
- `tipo_pago` define si es al CONTADO o en CUOTAS (solo esos dos).
- Al registrar un Pago se marca la Cuota como PAGADA y se recalcula la Venta.
"""

from decimal import Decimal

from django.conf import settings
from django.db import models

from shared.models import BaseModel

CERO = Decimal("0")


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

    def actualizar_estado(self):
        """Marca PAGADO cuando no queda saldo (no toca ventas anuladas)."""
        if self.estado == self.Estado.ANULADO:
            return
        nuevo = (
            self.Estado.PAGADO
            if self.total and self.saldo <= CERO
            else self.Estado.PENDIENTE
        )
        if nuevo != self.estado:
            self.estado = nuevo
            self.save(update_fields=["estado", "updated_at"])


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

    @property
    def total_pagado(self) -> Decimal:
        return sum((p.monto for p in self.pagos.all()), CERO)

    @property
    def saldo(self) -> Decimal:
        return (self.monto or CERO) - self.total_pagado

    def actualizar_estado(self):
        nuevo = (
            self.Estado.PAGADO
            if self.monto and self.saldo <= CERO
            else self.Estado.PENDIENTE
        )
        if nuevo != self.estado:
            self.estado = nuevo
            self.save(update_fields=["estado", "updated_at"])

    def __str__(self):
        return f"Cuota {self.numero}/{self.venta.cuotas.count()} - {self.venta}"


class Pago(BaseModel):
    """Pago (nota de pago) que solventa una cuota."""

    class Metodo(models.TextChoices):
        EFECTIVO = "EFECTIVO", "Efectivo"
        TARJETA = "TARJETA", "Tarjeta"
        TRANSFERENCIA = "TRANSFERENCIA", "Transferencia"
        YAPE = "YAPE", "Yape"
        PLIN = "PLIN", "Plin"
        OTRO = "OTRO", "Otro"

    cuota = models.ForeignKey(
        Cuota, on_delete=models.CASCADE, related_name="pagos"
    )
    monto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    metodo = models.CharField(
        max_length=15, choices=Metodo.choices, default=Metodo.EFECTIVO
    )
    fecha_pago = models.DateTimeField(null=True, blank=True)
    referencia = models.CharField(max_length=100, blank=True)
    comprobante = models.FileField(
        upload_to="ventas/comprobantes/%Y/%m/", null=True, blank=True
    )
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pagos_registrados",
    )

    # --- Validación del pago (reemplaza al modelo ValidacionPago) ---
    validado = models.BooleanField(default=False)
    validado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pagos_validados",
    )
    fecha_validacion = models.DateTimeField(null=True, blank=True)
    observacion_validacion = models.TextField(blank=True)

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ["-fecha_pago"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Al registrar un pago, recalcular estado de la cuota y de la venta.
        self.cuota.actualizar_estado()
        self.cuota.venta.actualizar_estado()

    def validar(self, usuario=None, observacion=""):
        """Marca el pago como validado por un usuario."""
        from django.utils import timezone

        self.validado = True
        self.validado_por = usuario
        self.fecha_validacion = timezone.now()
        if observacion:
            self.observacion_validacion = observacion
        self.save(update_fields=[
            "validado",
            "validado_por",
            "fecha_validacion",
            "observacion_validacion",
            "updated_at",
        ])
        return self

    def __str__(self):
        return f"Pago {self.monto} ({self.get_metodo_display()}) - cuota {self.cuota_id}"
