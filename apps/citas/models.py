"""
Modelos de la agenda dental.

- Medico: profesional que atiende.
- ServicioDental: catálogo de servicios/procedimientos.
- HorarioAtencion: franjas horarias de atención por médico (para ver
  disponibilidad).
- Cita: cita dental (con estados).
- Pago: pago(s) asociados a una cita.
"""

from django.conf import settings
from django.db import models

from shared.models import BaseModel


class Medico(BaseModel):
    """Profesional que atiende las citas."""

    # Vínculo opcional con un usuario del sistema (login).
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medico",
    )
    nombres = models.CharField(max_length=200)
    apellidos = models.CharField(max_length=200)
    especialidad = models.CharField(max_length=150, blank=True)
    colegiatura = models.CharField("N.º de colegiatura", max_length=50, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    correo = models.EmailField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Médico"
        verbose_name_plural = "Médicos"

    def __str__(self):
        return f"{self.nombres} {self.apellidos}".strip()


class ServicioDental(BaseModel):
    """
    Servicio o procedimiento dental. Soporta jerarquía: una categoría
    (``padre`` nulo) agrupa subservicios que la referencian por ``padre``.
    """

    padre = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subservicios",
    )
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duracion_minutos = models.PositiveIntegerField(
        "Duración estimada (min)", default=30
    )
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Servicio dental"
        verbose_name_plural = "Servicios dentales"
        ordering = ["nombre"]

    @property
    def es_categoria(self) -> bool:
        return self.padre_id is None

    def __str__(self):
        return self.nombre


class HorarioAtencion(BaseModel):
    """Franja horaria de atención de un médico (disponibilidad)."""

    class DiaSemana(models.IntegerChoices):
        LUNES = 0, "Lunes"
        MARTES = 1, "Martes"
        MIERCOLES = 2, "Miércoles"
        JUEVES = 3, "Jueves"
        VIERNES = 4, "Viernes"
        SABADO = 5, "Sábado"
        DOMINGO = 6, "Domingo"

    medico = models.ForeignKey(
        Medico, on_delete=models.CASCADE, related_name="horarios"
    )
    dia_semana = models.IntegerField(choices=DiaSemana.choices)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Horario de atención"
        verbose_name_plural = "Horarios de atención"
        ordering = ["dia_semana", "hora_inicio"]

    def __str__(self):
        return f"{self.medico} - {self.get_dia_semana_display()} {self.hora_inicio}-{self.hora_fin}"


class Cita(BaseModel):
    """Cita dental."""

    class Estado(models.TextChoices):
        PROGRAMADA = "PROGRAMADA", "Programada"
        CONFIRMADA = "CONFIRMADA", "Confirmada"
        EN_ATENCION = "EN_ATENCION", "En atención"
        ATENDIDA = "ATENDIDA", "Atendida"
        CANCELADA = "CANCELADA", "Cancelada"
        NO_ASISTIO = "NO_ASISTIO", "No asistió"

    paciente = models.ForeignKey(
        "pacientes.Paciente", on_delete=models.PROTECT, related_name="citas"
    )
    medico = models.ForeignKey(
        Medico, on_delete=models.PROTECT, related_name="citas"
    )
    servicio = models.ForeignKey(
        ServicioDental,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="citas",
    )
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField(null=True, blank=True)
    estado = models.CharField(
        max_length=15, choices=Estado.choices, default=Estado.PROGRAMADA
    )
    motivo = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        ordering = ["-fecha", "-hora_inicio"]

    def __str__(self):
        return f"Cita {self.fecha} {self.hora_inicio} - {self.paciente}"


class AtencionCita(BaseModel):
    """
    Detalle de la cita al ser atendida. Se crea cuando la cita se cierra
    (atendido / faltó / no pagó).
    """

    class Estado(models.TextChoices):
        ATENDIDO = "ATENDIDO", "Atendido"
        FALTO = "FALTO", "Faltó"
        NO_PAGO = "NO_PAGO", "No pagó (no se atendió)"

    cita = models.OneToOneField(
        Cita, on_delete=models.CASCADE, related_name="atencion"
    )
    fecha_cita = models.DateField()
    estado = models.CharField(
        max_length=10, choices=Estado.choices, default=Estado.ATENDIDO
    )
    descripcion = models.TextField("Descripción de la cita", blank=True)
    evolucion = models.TextField("Evolución del tratamiento", blank=True)
    medico_atendio = models.ForeignKey(
        Medico, on_delete=models.PROTECT, related_name="atenciones"
    )
    # Firma como texto por ahora; luego se reemplaza por firma digital.
    firma = models.TextField(blank=True)

    class Meta:
        verbose_name = "Atención de cita"
        verbose_name_plural = "Atenciones de cita"
        ordering = ["-fecha_cita"]

    def __str__(self):
        return f"Atención {self.get_estado_display()} - {self.cita}"
