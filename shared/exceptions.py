from django.db.models.deletion import ProtectedError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Maneja errores no cubiertos por DRF. En particular, convierte
    ProtectedError (borrar un registro referenciado por otros, p. ej. un
    paciente con citas/ventas/historia) en un 400 legible en vez de un 500.
    """
    if isinstance(exc, ProtectedError):
        return Response(
            {
                "detail": (
                    "No se puede eliminar: el registro tiene datos asociados "
                    "(citas, ventas o historia clínica). Quitá o reasigná esos "
                    "datos primero."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    return exception_handler(exc, context)
