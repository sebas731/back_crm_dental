from django.conf import settings
from django.db import models

from shared.models import BaseModel

from .cuota import Cuota


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
