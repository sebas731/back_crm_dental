from django.db import models

from shared.models import BaseModel

from .historia_clinica import HistoriaClinica


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
