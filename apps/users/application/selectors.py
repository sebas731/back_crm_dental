"""
Capa de LECTURA de la app users. Encapsula la visibilidad de usuarios según el
rol de quien consulta.
"""

from django.contrib.auth import get_user_model

from shared.permissions import ROLES_ADMINISTRATIVOS

User = get_user_model()


def user_list(*, solicitante):
    """
    Usuarios visibles para `solicitante`: los roles administrativos ven a todos;
    el resto solo se ve a sí mismo.
    """
    qs = User.objects.all().order_by("username")
    if getattr(solicitante, "rol", None) not in ROLES_ADMINISTRATIVOS:
        return qs.filter(pk=solicitante.pk)
    return qs
