"""
Modelos de dominio de la app `ventas`, separados en un archivo por modelo.
Este paquete re-exporta todo, así el resto del proyecto sigue importando con
`from apps.ventas.models import X`.

Jerarquía:
    Venta (nota de venta / cuenta del paciente)
      ├── VentaServicio  (1:N)  servicios aplicados (precio congelado)
      ├── Descuento      (1:N)  descuentos por monto o porcentaje
      ├── Adicional      (1:N)  materiales / insumos / extras (dinámico)
      └── Cuota          (1:N)  cronograma de pago (contado => 1 cuota)
             └── Pago    (1:N)  pagos que solventan la cuota

Reglas:
- La venta es como una "nota": una vez creada, lo editable es su `estado`
  (los montos/servicios se congelan/recalculan).
- `tipo_pago` define si es al CONTADO o en CUOTAS.
- Al registrar un Pago se marca la Cuota como PAGADA y se recalcula la Venta.
- Una venta con pagos validados (o anulada) se congela; para corregirla se
  duplica y se anula la original.
"""

from ._common import CERO, generar_numero_venta
from .adicional import Adicional
from .cuota import Cuota
from .descuento import Descuento
from .pago import Pago
from .venta import Venta
from .venta_servicio import VentaServicio

__all__ = [
    "CERO",
    "generar_numero_venta",
    "Venta",
    "VentaServicio",
    "Descuento",
    "Adicional",
    "Cuota",
    "Pago",
]
