"""
Capa de LECTURA de la app citas. Concentra las consultas (joins/prefetch y
filtros) para mantener las vistas finas.
"""

from ..models import Cita, NotaAgenda


def cita_list():
    """Citas con paciente, médico, servicio, venta y atención precargados."""
    return Cita.objects.select_related(
        "paciente", "medico", "servicio", "venta"
    ).prefetch_related("atencion")


def nota_list(*, fecha=None, desde=None, hasta=None):
    """Notas de agenda, filtradas por fecha exacta o por rango [desde, hasta]."""
    qs = NotaAgenda.objects.select_related("autor")
    if fecha:
        qs = qs.filter(fecha=fecha)
    if desde:
        qs = qs.filter(fecha__gte=desde)
    if hasta:
        qs = qs.filter(fecha__lte=hasta)
    return qs
