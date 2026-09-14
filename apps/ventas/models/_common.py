"""Utilidades compartidas por los modelos de ventas."""

import uuid
from decimal import Decimal

CERO = Decimal("0")


def generar_numero_venta() -> str:
    """Correlativo simple y único para una venta (p. ej. V-1A2B3C4D)."""
    return f"V-{uuid.uuid4().hex[:8].upper()}"
