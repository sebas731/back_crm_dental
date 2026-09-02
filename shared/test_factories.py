"""Factories mínimas para los tests (sin dependencias externas)."""

from decimal import Decimal

from django.contrib.auth import get_user_model

from apps.citas.models import Cita, Medico
from apps.pacientes.models import HistoriaClinica, Paciente
from apps.ventas.models import Cuota, Venta

User = get_user_model()

PASSWORD = "Prueba.Segura.2026"


def make_user(username, rol, password=PASSWORD):
    return User.objects.create_user(username=username, password=password, rol=rol)


def make_medico(nombres="Laura", apellidos="Díaz", usuario=None):
    return Medico.objects.create(nombres=nombres, apellidos=apellidos, usuario=usuario)


def make_paciente(numero_documento="12345678", nombres="Juan"):
    return Paciente.objects.create(
        nombre=nombres,
        apellido="Pérez",
        nombres=nombres,
        apellido_paterno="Pérez",
        sexo="M",
        tipo_documento="DNI",
        numero_documento=numero_documento,
    )


def make_historia(paciente, numero="HC-0001"):
    return HistoriaClinica.objects.create(paciente=paciente, numero=numero)


def make_venta_con_cuota(paciente, total="100.00"):
    venta = Venta.objects.create(paciente=paciente, total=Decimal(total))
    cuota = Cuota.objects.create(venta=venta, numero=1, monto=Decimal(total))
    return venta, cuota


def make_cita(medico, paciente, fecha="2031-05-10", hora="09:00", estado="PROGRAMADA"):
    return Cita.objects.create(
        medico=medico,
        paciente=paciente,
        fecha=fecha,
        hora_inicio=hora,
        estado=estado,
    )
