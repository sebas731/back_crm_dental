from django.db import models

from shared.models import BaseModel


class Insumo(BaseModel):
    """
    Insumo / producto de la clínica (batas, herramientas, materiales, etc.).
    Se relaciona muchos-a-muchos con los servicios que lo requieren.
    """

    nombre = models.CharField("Producto", max_length=150)
    unidad = models.CharField("Unidad", max_length=50)
    precio_unitario = models.DecimalField(
        "Precio unitario", max_digits=10, decimal_places=2, default=0
    )
    stock_actual = models.DecimalField(
        "Stock actual", max_digits=10, decimal_places=2, default=0
    )
    stock_minimo = models.DecimalField(
        "Stock mínimo", max_digits=10, decimal_places=2, default=0
    )
    comentario = models.TextField("Comentario", blank=True)

    class Meta:
        verbose_name = "Insumo"
        verbose_name_plural = "Insumos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
