"""
Capa de APLICACIÓN (casos de uso) de la app ventas.

Aquí viven las reglas de negocio de escritura: anular/duplicar una venta,
registrar y validar pagos, y los guardas de integridad de la cobranza. Las
vistas quedan finas y solo orquestan (parsean request → llaman a estos
servicios → responden).

Los servicios lanzan `django.core.exceptions.ValidationError`; el manejador de
excepciones del proyecto (shared/exceptions.py) lo traduce a un 400 de DRF, de
modo que esta capa no depende del framework web.
"""

from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Cuota, Pago, Venta

VENTA_BLOQUEADA = (
    "La venta está bloqueada (tiene pagos validados o está anulada) y no se "
    "pueden modificar sus servicios, adicionales ni descuentos. Duplicá la "
    "venta para corregirla y anulá la original."
)


# --- Venta -----------------------------------------------------------------
def venta_verificar_editable(venta: Venta | None) -> None:
    """Impide modificar los factores de una venta congelada."""
    if venta and not venta.editable:
        raise ValidationError(VENTA_BLOQUEADA)


def venta_recalcular(venta: Venta) -> None:
    """Recongela el total de la venta tras cambiar sus líneas."""
    venta.recalcular_total()


def venta_anular(*, venta: Venta, motivo: str = "") -> Venta:
    """Anula una venta (devoluciones / errores). Conserva su historial."""
    if venta.estado == Venta.Estado.ANULADO:
        raise ValidationError("La venta ya está anulada.")
    return venta.anular(motivo=motivo)


def venta_duplicar(*, original: Venta, usuario=None) -> Venta:
    """Crea una copia editable (sin pagos) para corregir una venta con errores."""
    return original.duplicar(usuario=usuario)


def venta_generar_para_cita(*, cita, usuario=None) -> Venta | None:
    """
    Genera la orden de venta (al CONTADO) de una cita que tiene servicio, para
    poder cobrarla y editarla. Si el servicio aún no tiene precio, la orden
    queda en S/ 0.00 lista para completar — no se atasca: actualizar_estado la
    resuelve según su saldo. Sin servicio, no crea nada.
    """
    from .models import VentaServicio

    if not cita.servicio_id:
        return None
    u = usuario if getattr(usuario, "is_authenticated", False) else None
    precio = cita.servicio.precio or 0
    venta = Venta.objects.create(
        cita=cita,
        paciente=cita.paciente,
        tipo_pago=Venta.TipoPago.CONTADO,
        total=precio,
        registrado_por=u,
    )
    VentaServicio.objects.create(
        venta=venta, servicio=cita.servicio, cantidad=1, precio_unitario=precio
    )
    return venta


# --- Cuota -----------------------------------------------------------------
def cuota_verificar_creacion(venta: Venta | None) -> None:
    if venta and not venta.editable:
        raise ValidationError(VENTA_BLOQUEADA)


def cuota_verificar_cambio_monto(*, cuota: Cuota, nuevo_monto) -> None:
    """No se puede cambiar el monto de una cuota que ya tiene pagos."""
    if (
        nuevo_monto is not None
        and nuevo_monto != cuota.monto
        and cuota.pagos.exists()
    ):
        raise ValidationError(
            "No se puede cambiar el monto de una cuota que ya tiene pagos."
        )


def cuota_verificar_eliminacion(cuota: Cuota) -> None:
    """Borrar la cuota arrastraría sus pagos (cascade). No permitido."""
    if cuota.pagos.exists():
        raise ValidationError(
            "No se puede eliminar una cuota que ya tiene pagos registrados. "
            "Anulá la venta si necesitás revertirla."
        )


# --- Pago ------------------------------------------------------------------
def pago_verificar_registrable(cuota: Cuota | None) -> None:
    if cuota and cuota.venta.estado == Venta.Estado.ANULADO:
        raise ValidationError(
            "No se pueden registrar pagos en una venta anulada."
        )


def pago_campos_registro(usuario) -> dict:
    """
    Campos que confirman un pago al registrarse (flujo de un solo paso: el pago
    queda pagado/validado en el acto, sin un paso aparte de 'validar').
    """
    u = usuario if getattr(usuario, "is_authenticated", False) else None
    return {
        "registrado_por": u,
        "validado": True,
        "validado_por": u,
        "fecha_validacion": timezone.now(),
    }


def pago_verificar_mutable(pago: Pago) -> None:
    """Un pago validado es inmutable (no se edita ni se borra)."""
    if pago.validado:
        raise ValidationError(
            "Un pago validado no se puede modificar ni eliminar. Anulá la "
            "venta si necesitás corregirlo."
        )


def pago_validar(*, pago: Pago, usuario=None, observacion: str = "") -> Pago:
    """Valida un pago. Idempotente: si ya está validado, no reescribe nada."""
    if pago.validado:
        return pago
    u = usuario if getattr(usuario, "is_authenticated", False) else None
    return pago.validar(usuario=u, observacion=observacion)
