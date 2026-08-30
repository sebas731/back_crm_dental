from rest_framework import serializers

from .models import Adicional, Cuota, Descuento, Pago, Venta, VentaServicio


class VentaServicioSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = VentaServicio
        fields = "__all__"


class DescuentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Descuento
        fields = "__all__"


class AdicionalSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Adicional
        fields = "__all__"


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = "__all__"
        # La validación se hace vía la acción /pagos/{id}/validar/.
        read_only_fields = ["validado", "validado_por", "fecha_validacion"]


class CuotaSerializer(serializers.ModelSerializer):
    pagos = PagoSerializer(many=True, read_only=True)
    total_pagado = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    saldo = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Cuota
        fields = "__all__"

    def validate(self, attrs):
        # No se puede reprogramar (cambiar la fecha de) una cuota ya pagada.
        if (
            self.instance
            and self.instance.estado == Cuota.Estado.PAGADO
            and "fecha_limite" in attrs
            and attrs["fecha_limite"] != self.instance.fecha_limite
        ):
            raise serializers.ValidationError(
                "No se puede reprogramar una cuota que ya está pagada."
            )
        return attrs


class VentaSerializer(serializers.ModelSerializer):
    servicios = VentaServicioSerializer(many=True, read_only=True)
    descuentos = DescuentoSerializer(many=True, read_only=True)
    adicionales = AdicionalSerializer(many=True, read_only=True)
    cuotas = CuotaSerializer(many=True, read_only=True)
    total_pagado = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    saldo = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    total_calculado = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Venta
        fields = "__all__"
