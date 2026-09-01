"""
Modelos de dominio: Cliente, Paciente, Acompanante, HistoriaClinica.

Relaciones:
- Paciente HEREDA de Cliente (herencia multi-tabla / MTI): un Paciente ES un
  Cliente. Cliente es el "interesado" del servicio; el Paciente es la
  especialización con todos los datos clínicos.
- Un Paciente tiene N Acompanante (FK).
- Un Paciente tiene una HistoriaClinica (OneToOne).

Nota: por ser MTI, Paciente NO puede redeclarar un campo con el mismo nombre
que Cliente. Por eso `correo` se hereda de Cliente (no se repite aquí), mientras
que `telefono` y `nombres` son campos propios del Paciente (nombres distintos a
`numero`/`nombre` de Cliente).
"""

from django.db import models

from shared.models import BaseModel


class Cliente(BaseModel):
    """Interesado en el servicio de atención (dato base que registran las empresas)."""

    nombre = models.CharField(max_length=150)
    apellido = models.CharField(max_length=150)
    segundo_apellido = models.CharField(max_length=150, blank=True)
    correo = models.EmailField(blank=True)
    numero = models.CharField("Número de contacto", max_length=30, blank=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return f"{self.nombre} {self.apellido}".strip()


class Paciente(Cliente):
    """Paciente: especialización de Cliente con la ficha de datos clínicos."""

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

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"

    def __str__(self):
        return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno}".strip()


class Acompanante(BaseModel):
    """Acompañante de un Paciente (dato extra)."""

    class Parentesco(models.TextChoices):
        PADRE = "PADRE", "Padre"
        MADRE = "MADRE", "Madre"
        HERMANO = "HERMANO", "Hermano/a"
        ABUELO = "ABUELO", "Abuelo/a"
        TIO = "TIO", "Tío/a"
        TUTOR = "TUTOR", "Tutor legal"
        OTRO = "OTRO", "Otro"

    paciente = models.ForeignKey(
        Paciente, on_delete=models.CASCADE, related_name="acompanantes"
    )
    nombre = models.CharField(max_length=150)
    apellido_paterno = models.CharField(max_length=150)
    apellido_materno = models.CharField(max_length=150, blank=True)
    dni = models.CharField(max_length=20)
    parentesco = models.CharField(max_length=10, choices=Parentesco.choices)
    telefono = models.CharField(max_length=30, blank=True)

    class Meta:
        verbose_name = "Acompañante"
        verbose_name_plural = "Acompañantes"

    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno} ({self.get_parentesco_display()})"


class HistoriaClinicaDetalle(BaseModel):
    """
    Detalle de la historia clínica. Se separa del modelo principal
    (referenciado por FK desde HistoriaClinica) para no engrosar la HC.

    Agrupa tres secciones de la ficha:
      3. Antecedentes personales y familiares
         - Revisión sistémica
      - Revisión local (examen intraoral)

    Cada campo es texto libre porque en la ficha corresponde a una línea de
    "especifique / indique".
    """

    # -- 3. Antecedentes personales y familiares --
    # 1. Alergia a algún medicamento, alimento o sustancia (especifique).
    alergias = models.TextField(blank=True)

    # 2. Enfermedades por aparatos o sistemas (especifique cuáles).
    pulmonares = models.TextField(blank=True)  # A. TBC, asma, influenza
    cardiacas = models.TextField(blank=True)  # B. Hipertensión, valvulopatías, soplo
    neurologicas = models.TextField(blank=True)  # C. Epilepsia, Parkinson, ausencias...
    hepaticas = models.TextField(blank=True)  # D. Ictericia, hepatitis, cirrosis
    renales = models.TextField(blank=True)  # E. Insuficiencia, cálculos, infecciones
    endocrino = models.TextField(blank=True)  # F. Diabetes, hipotiroidismo
    musculo_esqueletico = models.TextField(blank=True)  # G. Reuma, artritis, artrosis
    otras_enfermedades = models.TextField(blank=True)  # H. Otras

    # I. Enfermedad crónica y tratamiento que recibe.
    enfermedad_cronica_tratamiento = models.TextField(blank=True)
    # J. Cuenta con cartilla de vacunación completa.
    cartilla_vacunacion_completa = models.TextField(blank=True)
    # K. Existe algún problema de comportamiento.
    problema_comportamiento = models.TextField(blank=True)
    # L. Lactancia materna (tiempo, tipo).
    lactancia_materna = models.TextField(blank=True)
    # M. Experiencia dental previa (especificar).
    experiencia_dental_previa = models.TextField(blank=True)

    # Revisión sistémica (indicar lo restante).
    revision_sistemica = models.TextField(blank=True)

    # -- Revisión local (examen intraoral) --
    labios = models.TextField(blank=True)
    carrillos = models.TextField(blank=True)
    paladar_duro = models.TextField(blank=True)
    paladar_blando = models.TextField(blank=True)
    encias = models.TextField(blank=True)
    lengua = models.TextField(blank=True)
    piso_de_boca = models.TextField(blank=True)
    orofaringe = models.TextField(blank=True)
    atm = models.TextField("ATM (articulación temporomandibular)", blank=True)
    higiene = models.TextField(blank=True)

    class Meta:
        verbose_name = "Detalle de historia clínica"
        verbose_name_plural = "Detalles de historia clínica"

    def __str__(self):
        return f"Detalle HC {self.pk}"


class HistoriaClinica(BaseModel):
    """
    Historia clínica del paciente (modelo principal, liviano).

    El grueso de la ficha (antecedentes y revisiones) vive en
    `HistoriaClinicaDetalle`, referenciado por el FK `detalle`.
    """

    # PROTECT: borrar un paciente/cliente NO debe arrasar en silencio su
    # historia clínica (odontograma, antecedentes, documentos). Si tiene
    # historia, primero hay que eliminarla explícitamente.
    paciente = models.OneToOneField(
        Paciente, on_delete=models.PROTECT, related_name="historia_clinica"
    )
    numero = models.CharField(max_length=30, unique=True, blank=True)
    fecha_apertura = models.DateField(auto_now_add=True)
    observaciones = models.TextField(blank=True)

    # Detalle clínico propio de ESTA historia (1:1) — nunca compartido entre
    # pacientes. Puede quedar vacío hasta completar la ficha.
    detalle = models.OneToOneField(
        HistoriaClinicaDetalle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="historia",
    )

    class Meta:
        verbose_name = "Historia clínica"
        verbose_name_plural = "Historias clínicas"

    def __str__(self):
        return f"HC {self.numero or self.pk} - {self.paciente}"


class DocumentoHistoriaClinica(BaseModel):
    """
    Documento adjunto a una historia clínica (DNI, radiografía, consentimiento,
    receta, etc.). Una historia clínica puede tener varios documentos.
    """

    class Tipo(models.TextChoices):
        DNI = "DNI", "DNI / Documento de identidad"
        RADIOGRAFIA = "RADIOGRAFIA", "Radiografía"
        CONSENTIMIENTO = "CONSENTIMIENTO", "Consentimiento informado"
        RECETA = "RECETA", "Receta"
        RESULTADO = "RESULTADO", "Resultado de laboratorio"
        FOTOGRAFIA = "FOTOGRAFIA", "Fotografía clínica"
        OTRO = "OTRO", "Otro"

    historia_clinica = models.ForeignKey(
        HistoriaClinica, on_delete=models.CASCADE, related_name="documentos"
    )
    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.OTRO)
    titulo = models.CharField(max_length=200, blank=True)
    archivo = models.FileField(upload_to="historias/documentos/%Y/%m/")
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = "Documento de historia clínica"
        verbose_name_plural = "Documentos de historia clínica"

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.titulo or self.archivo.name}"


class Odontograma(BaseModel):
    """
    Odontograma asociado a una historia clínica. Se permite más de uno por
    historia (registro evolutivo).

    Los hallazgos por diente se guardan en `dientes` (JSON) usando la
    numeración FDI como clave, p. ej.:
        {"11": {"estado": "caries", "notas": "..."}, "36": {...}}
    Si más adelante querés charting relacional, esto se puede migrar a un
    modelo `OdontogramaDiente` (FK a Odontograma).
    """

    historia_clinica = models.ForeignKey(
        HistoriaClinica, on_delete=models.CASCADE, related_name="odontogramas"
    )
    fecha = models.DateField(auto_now_add=True)

    # Hallazgos por pieza dental (numeración FDI).
    dientes = models.JSONField(default=dict, blank=True)

    # Campos del pie de la ficha.
    especificaciones = models.TextField(blank=True)
    informe_radiografico = models.TextField(blank=True)
    higiene_bucal = models.TextField(blank=True)
    ihos = models.TextField("IHOS", blank=True)
    diagnostico = models.TextField(blank=True)
    cie = models.CharField("CIE", max_length=20, blank=True)
    plan_tratamiento = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Odontograma"
        verbose_name_plural = "Odontogramas"

    def __str__(self):
        return f"Odontograma {self.fecha} - {self.historia_clinica}"


class AntecedentesPersonales(BaseModel):
    """
    Antecedentes personales y familiares (sección 3 de la ficha).
    Relacionado 1:1 con la historia clínica.
    """

    historia_clinica = models.OneToOneField(
        HistoriaClinica,
        on_delete=models.CASCADE,
        related_name="antecedentes",
    )

    # 1. Alergias
    alergias = models.TextField(
        blank=True,
        null=True,
        help_text="Alergia a algún medicamento, alimento o sustancia (especificar)",
    )

    # 2. Enfermedades por sistemas/aparatos
    enfermedades_pulmonares = models.TextField(
        blank=True, null=True, help_text="TBC, asma, influenza, etc."
    )
    enfermedades_cardiacas = models.TextField(
        blank=True, null=True, help_text="Hipertensión, valvulopatías, soplo, etc."
    )
    enfermedades_neurologicas = models.TextField(
        blank=True,
        null=True,
        help_text="Epilepsia, Parkinson, ausencias, trastornos mentales, emocionales o nerviosos",
    )
    enfermedades_hepaticas = models.TextField(
        blank=True, null=True, help_text="Ictericia, hepatitis, cirrosis, etc."
    )
    enfermedades_renales = models.TextField(
        blank=True, null=True, help_text="Insuficiencia, cálculos, infecciones, etc."
    )
    sistema_endocrino = models.TextField(
        blank=True, null=True, help_text="Diabetes, hipotiroidismo, etc."
    )
    musculo_esqueletico = models.TextField(
        blank=True, null=True, help_text="Reuma, artritis, artrosis, etc."
    )
    otras_enfermedades = models.TextField(
        blank=True, null=True, help_text="Otras enfermedades no especificadas arriba"
    )

    # Detalle de afecciones crónicas, conducta e historial
    enfermedad_cronica_y_tratamiento = models.TextField(
        blank=True,
        null=True,
        help_text="Enfermedad crónica que padece y tratamiento que recibe",
    )
    cartilla_vacunacion_completa = models.BooleanField(
        default=False, help_text="¿Cuenta con cartilla de vacunación completa?"
    )
    problema_comportamiento = models.TextField(
        blank=True, null=True, help_text="Problemas de comportamiento (especificar)"
    )
    lactancia_materna = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Tiempo y tipo de lactancia materna",
    )
    experiencia_dental_previa = models.TextField(
        blank=True, null=True, help_text="Experiencia dental previa (especificar)"
    )

    # Sección de revisión final
    revision_sistemica = models.TextField(
        blank=True, null=True, help_text="Revisión sistémica (indicar lo restante)"
    )

    class Meta:
        verbose_name = "Antecedentes personales"
        verbose_name_plural = "Antecedentes personales"

    def __str__(self):
        return f"Antecedentes de {self.historia_clinica}"
