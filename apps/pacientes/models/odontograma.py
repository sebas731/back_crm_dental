from django.db import models

from shared.models import BaseModel

from .historia_clinica import HistoriaClinica


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
