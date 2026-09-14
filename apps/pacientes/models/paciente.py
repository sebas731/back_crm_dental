from django.db import models

from .cliente import Cliente


class Paciente(Cliente):
    """Paciente: especialización de Cliente con la ficha de datos clínicos.

    Por ser herencia multi-tabla (MTI), un Paciente ES un Cliente y NO puede
    redeclarar un campo con el mismo nombre que Cliente. Por eso `correo` se
    hereda de Cliente (no se repite aquí), mientras que `telefono` y `nombres`
    son campos propios (nombres distintos a `numero`/`nombre` de Cliente).
    """

    class Sexo(models.TextChoices):
        MASCULINO = "M", "Masculino"
        FEMENINO = "F", "Femenino"

    class TipoDocumento(models.TextChoices):
        DNI = "DNI", "DNI"
        CARNE_EXTRANJERIA = "CE", "Carné de extranjería"
        PASAPORTE = "PAS", "Pasaporte"
        PARTIDA_NACIMIENTO = "PART", "Partida de nacimiento"

    class GrupoSanguineo(models.TextChoices):
        A_POS = "A+", "A+"
        A_NEG = "A-", "A-"
        B_POS = "B+", "B+"
        B_NEG = "B-", "B-"
        AB_POS = "AB+", "AB+"
        AB_NEG = "AB-", "AB-"
        O_POS = "O+", "O+"
        O_NEG = "O-", "O-"

    class Procedencia(models.TextChoices):
        TIKTOK = "TIKTOK", "TikTok"
        FACEBOOK = "FACEBOOK", "Facebook"
        INSTAGRAM = "INSTAGRAM", "Instagram"
        WHATSAPP = "WHATSAPP", "WhatsApp"
        GOOGLE = "GOOGLE", "Google / búsqueda web"
        RECOMENDADO = "RECOMENDADO", "Recomendado por un paciente"
        FERIA = "FERIA", "Feria / campaña"
        PASO = "PASO", "Pasó por el local"
        OTRO = "OTRO", "Otro"

    # --- Marketing / captación ---
    procedencia = models.CharField(
        "¿De dónde viene el paciente?",
        max_length=15,
        choices=Procedencia.choices,
        blank=True,
    )

    # --- Datos personales ---
    apellido_paterno = models.CharField(max_length=150)
    apellido_materno = models.CharField(max_length=150, blank=True)
    nombres = models.CharField(max_length=200)
    sexo = models.CharField(max_length=1, choices=Sexo.choices)
    edad = models.PositiveIntegerField(null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)

    # --- Documento de identidad ---
    tipo_documento = models.CharField(
        max_length=4, choices=TipoDocumento.choices, default=TipoDocumento.DNI
    )
    numero_documento = models.CharField(max_length=20, unique=True)

    # --- Datos clínicos / contexto ---
    grupo_sanguineo = models.CharField(
        max_length=3, choices=GrupoSanguineo.choices, blank=True
    )
    centro_educativo = models.CharField(max_length=200, blank=True)
    nombre_padre = models.CharField(max_length=200, blank=True)
    nombre_madre = models.CharField(max_length=200, blank=True)

    # --- Contacto ---
    # `correo` se hereda de Cliente.
    direccion = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    # Número al que se envían los mensajes de WhatsApp (si difiere del teléfono).
    whatsapp = models.CharField("Número de WhatsApp", max_length=30, blank=True)

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"

    def __str__(self):
        return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno}".strip()
