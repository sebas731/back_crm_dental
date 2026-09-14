"""
Capa de APLICACIÓN (casos de uso) de la app ventas.

Aquí viven las reglas de negocio de escritura: anular/duplicar una venta,
registrar y validar pagos, y los guardas de integridad de la cobranza. Las
vistas quedan finas y solo orquestan (parsean request → llaman a estos
servicios → responden).

Los servicios lanzan las excepciones de dominio de `apps.ventas.exceptions`
(subclases de la `ValidationError` de Django); el manejador del proyecto
(shared/exceptions.py) las traduce a un 400 de DRF, de modo que esta capa no
depende del framework web.
"""

from django.db import transaction
from django.utils import timezone

from .. import exceptions
from ..models import Cuota, Pago, Venta


# --- Venta -----------------------------------------------------------------
def venta_verificar_editable(venta: Venta | None) -> None:
    """Impide modificar los factores de una venta congelada."""
    if venta and not venta.editable:
        raise exceptions.VentaBloqueada()


def venta_recalcular(venta: Venta) -> None:
    """Recongela el total de la venta tras cambiar sus líneas."""
    venta.recalcular_total()


def venta_anular(*, venta: Venta, motivo: str = "") -> Venta:
    """Anula una venta (devoluciones / errores). Conserva su historial."""
    if venta.estado == Venta.Estado.ANULADO:
        raise exceptions.VentaYaAnulada()
    return venta.anular(motivo=motivo)


def venta_duplicar(*, original: Venta, usuario=None) -> Venta:
    """
    Crea una copia editable (nueva venta PENDIENTE) con los mismos factores y
    cronograma que `original`, pero SIN pagos ni validaciones. Sirve para
    rehacer una venta registrada con errores. Es un caso de uso (crea varios
    registros relacionados), por eso vive acá y no en el modelo.
    """
    from ..models import Adicional, Cuota, Descuento, VentaServicio

    with transaction.atomic():
        nueva = Venta.objects.create(
            paciente=original.paciente,
            tipo_pago=original.tipo_pago,
            observaciones=original.observaciones,
            registrado_por=usuario,
            estado=Venta.Estado.PENDIENTE,
        )
        for s in original.servicios.all():
            VentaServicio.objects.create(
                venta=nueva,
                servicio=s.servicio,
                cantidad=s.cantidad,
                precio_unitario=s.precio_unitario,
            )
        for d in original.descuentos.all():
            Descuento.objects.create(
                venta=nueva,
                descripcion=d.descripcion,
                tipo=d.tipo,
                valor=d.valor,
            )
        for a in original.adicionales.all():
            Adicional.objects.create(
                venta=nueva,
                nombre=a.nombre,
                tipo=a.tipo,
                valor=a.valor,
                cantidad=a.cantidad,
            )
        for c in original.cuotas.all():
            Cuota.objects.create(
                venta=nueva,
                numero=c.numero,
                monto=c.monto,
                fecha_limite=c.fecha_limite,
            )
        nueva.recalcular_total()
    return nueva


def venta_generar_para_cita(*, cita, usuario=None) -> Venta | None:
    """
    Genera la orden de venta (al CONTADO) de una cita que tiene servicio, para
    poder cobrarla y editarla. Si el servicio aún no tiene precio, la orden
    queda en S/ 0.00 lista para completar — no se atasca: actualizar_estado la
    resuelve según su saldo. Sin servicio, no crea nada.
    """
    from ..models import VentaServicio

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
        raise exceptions.VentaBloqueada()


def cuota_verificar_cambio_monto(*, cuota: Cuota, nuevo_monto) -> None:
    """No se puede cambiar el monto de una cuota que ya tiene pagos."""
    if (
        nuevo_monto is not None
        and nuevo_monto != cuota.monto
        and cuota.pagos.exists()
    ):
        raise exceptions.CuotaMontoConPagos()


def cuota_verificar_eliminacion(cuota: Cuota) -> None:
    """Borrar la cuota arrastraría sus pagos (cascade). No permitido."""
    if cuota.pagos.exists():
        raise exceptions.CuotaConPagos()


# --- Pago ------------------------------------------------------------------
def pago_verificar_registrable(cuota: Cuota | None) -> None:
    if cuota and cuota.venta.estado == Venta.Estado.ANULADO:
        raise exceptions.PagoEnVentaAnulada()


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
        raise exceptions.PagoInmutable()


def pago_validar(*, pago: Pago, usuario=None, observacion: str = "") -> Pago:
    """Valida un pago. Idempotente: si ya está validado, no reescribe nada."""
    if pago.validado:
        return pago
    u = usuario if getattr(usuario, "is_authenticated", False) else None
    return pago.validar(usuario=u, observacion=observacion)
