"""
Excepciones de dominio de ventas.

Nombran cada regla de negocio de cobranza para que la capa de aplicación
(services) sea legible y que el error salga con un mensaje claro. Heredan de la
`ValidationError` de Django; el manejador del proyecto (shared/exceptions.py) la
traduce a un 400 de DRF.
"""

from django.core.exceptions import ValidationError


class VentaBloqueada(ValidationError):
    def __init__(self):
        super().__init__(
            "La venta está bloqueada (tiene pagos validados o está anulada) y "
            "no se pueden modificar sus servicios, adicionales ni descuentos. "
            "Duplicá la venta para corregirla y anulá la original."
        )


class VentaYaAnulada(ValidationError):
    def __init__(self):
        super().__init__("La venta ya está anulada.")


class PagoEnVentaAnulada(ValidationError):
    def __init__(self):
        super().__init__("No se pueden registrar pagos en una venta anulada.")


class PagoInmutable(ValidationError):
    def __init__(self):
        super().__init__(
            "Un pago validado no se puede modificar ni eliminar. Anulá la "
            "venta si necesitás corregirlo."
        )


class CuotaConPagos(ValidationError):
    def __init__(self):
        super().__init__(
            "No se puede eliminar una cuota que ya tiene pagos registrados. "
            "Anulá la venta si necesitás revertirla."
        )


class CuotaMontoConPagos(ValidationError):
    def __init__(self):
        super().__init__(
            "No se puede cambiar el monto de una cuota que ya tiene pagos."
        )
