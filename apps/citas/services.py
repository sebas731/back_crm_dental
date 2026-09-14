"""
Capa de APLICACIÓN (casos de uso) de la app citas: agendar una cita (con su
orden de venta) y registrar la atención. Mantiene la lógica fuera de las vistas.
"""

from apps.ventas.services import venta_generar_para_cita

from .models import AtencionCita, Cita


def cita_generar_orden(*, cita: Cita, usuario=None):
    """Genera la orden de venta de la cita si tiene servicio (delegada a ventas)."""
    return venta_generar_para_cita(cita=cita, usuario=usuario)


# Mapeo del estado de la atención al estado de la cita.
_ESTADO_CITA_POR_ATENCION = {
    AtencionCita.Estado.ATENDIDO: Cita.Estado.ATENDIDA,
    AtencionCita.Estado.FALTO: Cita.Estado.NO_ASISTIO,
    # NO_PAGO / cualquier otro → CANCELADA
}


def cita_aplicar_atencion(*, cita: Cita, estado_atencion: str) -> Cita:
    """Sincroniza el estado de la cita según el resultado de la atención."""
    cita.estado = _ESTADO_CITA_POR_ATENCION.get(
        estado_atencion, Cita.Estado.CANCELADA
    )
    cita.save(update_fields=["estado", "updated_at"])
    return cita
