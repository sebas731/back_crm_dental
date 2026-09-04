from decimal import Decimal

from rest_framework import serializers

from shared.validators import validar_archivo

from .models import Adicional, Cuota, Descuento, Pago, Venta, VentaServicio

CERO = Decimal("0")


class VentaServicioSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = VentaServicio
        fields = "__all__"

    def validate_precio_unitario(self, value):
        if value is not None and value < CERO:
            raise serializers.ValidationError("El precio no puede ser negativo.")
        return value

    def validate_cantidad(self, value):
        if value is not None and value < 1:
            raise serializers.ValidationError("La cantidad debe ser al menos 1.")
        return value


class DescuentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Descuento
        fields = "__all__"

    def validate(self, attrs):
        tipo = attrs.get("tipo") or getattr(self.instance, "tipo", None)
        valor = attrs.get("valor")
        if valor is None:
            valor = getattr(self.instance, "valor", None)
        if valor is not None:
            if valor < CERO:
                raise serializers.ValidationError(
                    "El descuento no puede ser negativo."
                )
            if tipo == Descuento.Tipo.PORCENTAJE and valor > Decimal("100"):
                raise serializers.ValidationError(
                    "Un descuento porcentual no puede superar el 100%."
                )
        return attrs


class AdicionalSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Adicional
        fields = "__all__"

    def validate_valor(self, value):
        if value is not None and value < CERO:
            raise serializers.ValidationError("El valor no puede ser negativo.")
        return value

    def validate_cantidad(self, value):
        if value is not None and value < 1:
            raise serializers.ValidationError("La cantidad debe ser al menos 1.")
        return value


class PagoSerializer(serializers.ModelSerializer):
    registrado_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Pago
        fields = "__all__"
        # La validación se hace vía la acción /pagos/{id}/validar/.
        read_only_fields = ["validado", "validado_por", "fecha_validacion"]

    def get_registrado_por_nombre(self, obj):
        u = obj.registrado_por
        if not u:
            return ""
        nombre = f"{u.first_name} {u.last_name}".strip()
        return nombre or u.username

    def validate_comprobante(self, value):
        return validar_archivo(value)

    def validate(self, attrs):
        monto = attrs.get("monto")
        if monto is None:
            monto = getattr(self.instance, "monto", None)
        cuota = attrs.get("cuota") or getattr(self.instance, "cuota", None)
        if monto is not None:
            if monto <= CERO:
                raise serializers.ValidationError(
                    {"monto": "El monto del pago debe ser mayor que cero."}
                )
            # No se puede pagar más de lo que se debe en la cuota.
            if cuota is not None:
                # Al editar, descontar el propio pago del total ya pagado.
                ya_pagado = cuota.total_pagado
                if self.instance is not None:
                    ya_pagado -= self.instance.monto
                disponible = (cuota.monto or CERO) - ya_pagado
                if monto > disponible:
                    raise serializers.ValidationError(
                        {
                            "monto": (
                                f"El monto excede el saldo de la cuota "
                                f"(disponible S/ {disponible})."
                            )
                        }
                    )
        return attrs


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
        # El estado se deriva de los pagos (actualizar_estado); no se escribe
        # a mano. Antes cualquier rol podía forzar estado=PAGADO sin pagar.
        read_only_fields = ["estado"]

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
    editable = serializers.BooleanField(read_only=True)
    tiene_pagos_validados = serializers.BooleanField(read_only=True)

    class Meta:
        model = Venta
        fields = "__all__"
        # El número se genera en el servidor (único); no se acepta del cliente.
        read_only_fields = ["numero"]
