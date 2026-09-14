from django.db import models

from shared.models import BaseModel

from .historia_clinica import HistoriaClinica


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
