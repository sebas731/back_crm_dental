from django.db import models

from shared.models import BaseModel


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
