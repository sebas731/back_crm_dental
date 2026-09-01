"""
Carga datos de prueba para DENTAL SAC.

Uso:
    python manage.py seed_demo          # crea/asegura los datos demo
    python manage.py seed_demo --reset  # borra los datos demo y los recrea

Crea: usuario admin (admin/admin1234), médicos, servicios, horarios,
pacientes, citas (con distintos estados), pagos + validaciones y atenciones.
"""

from datetime import date, time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.citas.catalog import crear_catalogo
from apps.citas.models import (
    AtencionCita,
    Cita,
    HorarioAtencion,
    Medico,
    ServicioDental,
)
from apps.pacientes.models import HistoriaClinica, Paciente
from apps.ventas.models import Cuota, Pago, Venta, VentaServicio

User = get_user_model()


class Command(BaseCommand):
    help = "Carga datos de prueba para probar el CRM."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Borra los datos demo antes de recrearlos.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            self.stdout.write("Borrando datos demo…")
            Pago.objects.all().delete()
            Cuota.objects.all().delete()
            Venta.objects.all().delete()
            AtencionCita.objects.all().delete()
            Cita.objects.all().delete()
            HorarioAtencion.objects.all().delete()
            HistoriaClinica.objects.all().delete()
            Paciente.objects.all().delete()
            Medico.objects.all().delete()
            ServicioDental.objects.all().delete()

        # --- Usuario admin ---
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@dentalsac.com", "rol": "ADMIN"},
        )
        if created:
            admin.set_password("admin1234")
            admin.is_staff = True
            admin.is_superuser = True
            admin.first_name = "Admin"
            admin.last_name = "DENTAL STUDIO"
            admin.save()
            self.stdout.write("  Usuario admin creado (admin / admin1234)")

        # --- Usuario asistente (rol ASSISTANT) ---
        asis, a_created = User.objects.get_or_create(
            username="asistente",
            defaults={"email": "asistente@dentalstudio.com", "rol": "ASSISTANT"},
        )
        if a_created:
            asis.set_password("asistente123")
            asis.first_name = "Ana"
            asis.last_name = "Asistente"
            asis.save()
            self.stdout.write("  Usuario asistente creado (asistente / asistente123)")

        # --- Médicos ---
        medicos_data = [
            ("Laura", "Quispe", "Ortodoncia", "COP-1001"),
            ("Diego", "Ramos", "Endodoncia", "COP-1002"),
            ("Carmen", "Flores", "Odontopediatría", "COP-1003"),
        ]
        medicos = []
        for nombres, apellidos, esp, col in medicos_data:
            m, _ = Medico.objects.get_or_create(
                colegiatura=col,
                defaults={
                    "nombres": nombres,
                    "apellidos": apellidos,
                    "especialidad": esp,
                    "telefono": "999000111",
                    "correo": f"{nombres.lower()}@dentalstudio.com",
                },
            )
            # Usuario médico vinculado (login: <nombre> / medico123)
            uname = nombres.lower()
            u, u_created = User.objects.get_or_create(
                username=uname,
                defaults={
                    "email": f"{uname}@dentalstudio.com",
                    "rol": "MEDICO",
                    "first_name": nombres,
                    "last_name": apellidos,
                },
            )
            if u_created:
                u.set_password("medico123")
                u.save()
            if m.usuario_id is None:
                m.usuario = u
                m.save(update_fields=["usuario"])
            medicos.append(m)

        # --- Horarios de atención (Lun-Vie) ---
        for m in medicos:
            for dia in range(0, 5):  # Lunes(0) a Viernes(4)
                HorarioAtencion.objects.get_or_create(
                    medico=m,
                    dia_semana=dia,
                    hora_inicio=time(9, 0),
                    hora_fin=time(13, 0),
                )
                HorarioAtencion.objects.get_or_create(
                    medico=m,
                    dia_semana=dia,
                    hora_inicio=time(15, 0),
                    hora_fin=time(19, 0),
                )

        # --- Servicios (catálogo real) ---
        crear_catalogo()
        # Para las citas usamos subservicios (hojas) con un precio de ejemplo.
        servicios = list(
            ServicioDental.objects.filter(padre__isnull=False).order_by("nombre")
        )
        precios_demo = ["45", "80", "120", "350", "150"]
        for i, s in enumerate(servicios[:5]):
            if not s.precio:
                s.precio = Decimal(precios_demo[i % len(precios_demo)])
                s.save(update_fields=["precio"])
        servicios = servicios[:5] or list(ServicioDental.objects.all()[:5])

        # --- Pacientes (+ historia clínica) ---
        pacientes_data = [
            ("Mateo", "Torres", "Vega", "M", "12345678", "O+", "TIKTOK"),
            ("Sofía", "Díaz", "Ríos", "F", "23456789", "A+", "FACEBOOK"),
            ("Lucas", "Mendoza", "Cruz", "M", "34567890", "B+", "INSTAGRAM"),
            ("Valentina", "Rojas", "León", "F", "45678901", "AB+", "RECOMENDADO"),
            ("Benjamín", "Castro", "Soto", "M", "56789012", "O-", "GOOGLE"),
        ]
        pacientes = []
        for nombres, ap_pat, ap_mat, sexo, dni, grupo, origen in pacientes_data:
            p, _ = Paciente.objects.get_or_create(
                numero_documento=dni,
                defaults={
                    "nombre": nombres,
                    "apellido": ap_pat,
                    "nombres": nombres,
                    "apellido_paterno": ap_pat,
                    "apellido_materno": ap_mat,
                    "sexo": sexo,
                    "tipo_documento": "DNI",
                    "grupo_sanguineo": grupo,
                    "procedencia": origen,
                    "telefono": "988777666",
                    "correo": f"{nombres.lower()}@example.com",
                    "direccion": "Av. Siempre Viva 123",
                },
            )
            HistoriaClinica.objects.get_or_create(
                paciente=p, defaults={"numero": f"HC-{dni[-4:]}"}
            )
            pacientes.append(p)

        # --- Citas (repartidas alrededor de hoy) ---
        hoy = date.today()
        estados = [
            Cita.Estado.PROGRAMADA,
            Cita.Estado.CONFIRMADA,
            Cita.Estado.ATENDIDA,
            Cita.Estado.NO_ASISTIO,
            Cita.Estado.CANCELADA,
        ]
        horas = [time(9, 0), time(10, 30), time(12, 0), time(15, 30), time(17, 0)]
        citas = []
        for i in range(10):
            paciente = pacientes[i % len(pacientes)]
            medico = medicos[i % len(medicos)]
            servicio = servicios[i % len(servicios)]
            fecha = hoy + timedelta(days=(i - 3))  # de -3 a +6 días
            cita, _ = Cita.objects.get_or_create(
                paciente=paciente,
                medico=medico,
                fecha=fecha,
                hora_inicio=horas[i % len(horas)],
                defaults={
                    "servicio": servicio,
                    "estado": estados[i % len(estados)],
                    "motivo": f"{servicio.nombre}",
                },
            )
            citas.append((cita, servicio))

        # --- Ventas + cuotas + pagos + atenciones para citas atendidas ---
        for cita, servicio in citas:
            if cita.estado == Cita.Estado.ATENDIDA:
                precio = servicio.precio or Decimal("100")
                venta, creada = Venta.objects.get_or_create(
                    numero=f"V-{cita.pk.hex[:8]}",
                    defaults={
                        "paciente": cita.paciente,
                        "cita": cita,
                        "tipo_pago": Venta.TipoPago.CONTADO,
                        "total": precio,
                        "registrado_por": admin,
                    },
                )
                if creada:
                    VentaServicio.objects.create(
                        venta=venta,
                        servicio=servicio,
                        cantidad=1,
                        precio_unitario=precio,
                    )
                    cuota = Cuota.objects.create(
                        venta=venta,
                        numero=1,
                        monto=precio,
                        fecha_limite=cita.fecha,
                        cita=cita,
                    )
                    pago = Pago.objects.create(
                        cuota=cuota,
                        monto=precio,
                        metodo=Pago.Metodo.YAPE,
                        fecha_pago=timezone.now(),
                        referencia="OP-SEED",
                    )
                    pago.validar(usuario=admin)

                AtencionCita.objects.get_or_create(
                    cita=cita,
                    defaults={
                        "fecha_cita": cita.fecha,
                        "estado": AtencionCita.Estado.ATENDIDO,
                        "descripcion": f"Se realizó {servicio.nombre}.",
                        "evolucion": "Paciente evoluciona favorablemente.",
                        "medico_atendio": cita.medico,
                        "firma": f"Dr(a). {cita.medico.nombres} {cita.medico.apellidos}",
                    },
                )
            elif cita.estado == Cita.Estado.NO_ASISTIO:
                AtencionCita.objects.get_or_create(
                    cita=cita,
                    defaults={
                        "fecha_cita": cita.fecha,
                        "estado": AtencionCita.Estado.FALTO,
                        "descripcion": "El paciente no se presentó.",
                        "medico_atendio": cita.medico,
                    },
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed OK: {Medico.objects.count()} médicos, "
                f"{ServicioDental.objects.count()} servicios, "
                f"{Paciente.objects.count()} pacientes, "
                f"{Cita.objects.count()} citas, "
                f"{Pago.objects.count()} pagos, "
                f"{AtencionCita.objects.count()} atenciones."
            )
        )
