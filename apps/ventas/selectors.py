"""
Capa de LECTURA de la app ventas.

Los selectors concentran las consultas (querysets, joins, prefetch) para que
las vistas no armen ORM a mano y para poder reutilizarlas/optimizarlas en un
solo lugar. No modifican datos.
"""

from .models import Cuota, Pago, Venta


def venta_list():
    """Ventas con todo lo necesario para serializarlas sin N+1."""
    return Venta.objects.select_related("paciente").prefetch_related(
        "servicios", "descuentos", "adicionales", "cuotas__pagos"
    )


def cuota_list():
    """Cuotas con su venta y pagos precargados."""
    return Cuota.objects.select_related("venta").prefetch_related("pagos")


def pago_list():
    """Pagos con su cuota precargada."""
    return Pago.objects.select_related("cuota")
