from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

ROLES_ADMINISTRATIVOS = {"ADMIN", "MANAGER"}
# Roles que pueden gestionar datos clínicos/agenda (el médico solo consulta).
ROLES_CLINICOS = {"ADMIN", "MANAGER", "ASSISTANT"}


def _rol(request):
    return getattr(request.user, "rol", None)


class PuedeGestionarPagos(permissions.BasePermission):
    """
    Lectura permitida a cualquier usuario autenticado.
    Escritura (registrar/validar pagos, gestionar ventas/cuotas) solo para
    roles administrativos; el asistente no puede registrar ni validar pagos.
    """

    message = "No tenés permiso para registrar o validar pagos."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return _rol(request) in ROLES_ADMINISTRATIVOS


class GestionClinica(permissions.BasePermission):
    """
    Pacientes, citas, historias clínicas, odontogramas, documentos, etc.
    - Lectura: cualquier usuario autenticado.
    - Crear/editar (POST/PUT/PATCH): admin, manager y asistente.
    - Borrar (DELETE): solo administrativos (admin/manager).
    El médico solo consulta: no crea, edita ni borra estos registros
    (su vía de escritura clínica es la acción "atender" de la cita).
    """

    message = "Tu rol no permite modificar estos datos clínicos."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        rol = _rol(request)
        if request.method == "DELETE":
            return rol in ROLES_ADMINISTRATIVOS
        return rol in ROLES_CLINICOS


class SoloAdministrativos(permissions.BasePermission):
    """
    Lectura para cualquier autenticado; escritura solo admin/manager.
    Para catálogos y configuración (médicos, servicios, horarios).
    """

    message = "Solo un administrador puede modificar esta configuración."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return _rol(request) in ROLES_ADMINISTRATIVOS


class GestionAgenda(permissions.BasePermission):
    """
    Notas de agenda: admin, manager y asistente (todas las operaciones).
    El médico no accede a las notas.
    """

    message = "Tu rol no permite gestionar notas de agenda."

    def has_permission(self, request, view):
        return _rol(request) in ROLES_CLINICOS


class GestionUsuarios(permissions.BasePermission):
    """
    - Crear/listar/borrar usuarios: solo administrativos.
    - Un usuario puede ver y editar su propia cuenta, pero NO su rol ni sus
      flags de acceso (eso lo controla el serializer).
    """

    message = "No tenés permiso para gestionar este usuario."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        # Crear usuarios: solo administrativos.
        if request.method == "POST":
            return _rol(request) in ROLES_ADMINISTRATIVOS
        return True

    def has_object_permission(self, request, view, obj):
        rol = _rol(request)
        if rol in ROLES_ADMINISTRATIVOS:
            return True
        # Borrar: solo administrativos.
        if request.method == "DELETE":
            return False
        # Un usuario común solo puede operar sobre su propia cuenta.
        return obj.pk == request.user.pk
