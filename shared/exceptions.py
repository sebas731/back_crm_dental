from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models.deletion import ProtectedError
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response
from rest_framework.serializers import as_serializer_error
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Maneja errores no cubiertos por DRF:

    - ValidationError de Django (la que lanzan los services de la capa de
      aplicación) se convierte en un 400 con el formato de errores de DRF, para
      que la lógica de negocio no dependa de las excepciones del framework web.
    - ProtectedError (borrar un registro referenciado por otros, p. ej. un
      paciente con citas/ventas/historia) se convierte en un 400 legible en vez
      de un 500.
    """
    if isinstance(exc, DjangoValidationError):
        exc = DRFValidationError(as_serializer_error(exc))
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
