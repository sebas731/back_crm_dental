from rest_framework import serializers

from shared.validators import validar_archivo

from .models import (
    Acompanante,
    AntecedentesPersonales,
    Cliente,
    DocumentoHistoriaClinica,
    HistoriaClinica,
    HistoriaClinicaDetalle,
    Odontograma,
    Paciente,
)

# Longitud esperada del número de documento por tipo (None = sin regla fija).
LONGITUD_DOCUMENTO = {"DNI": 8}


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = "__all__"


class AcompananteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acompanante
        fields = "__all__"


class PacienteSerializer(serializers.ModelSerializer):
    # Lectura anidada de acompañantes (escritura vía endpoint /acompanantes/).
    acompanantes = AcompananteSerializer(many=True, read_only=True)

    class Meta:
        model = Paciente
        fields = "__all__"

    def validate(self, attrs):
        tipo = attrs.get("tipo_documento") or getattr(
            self.instance, "tipo_documento", None
        )
        numero = attrs.get("numero_documento")
        if numero is None:
            numero = getattr(self.instance, "numero_documento", None)
        if tipo and numero:
            largo = LONGITUD_DOCUMENTO.get(tipo)
            # El DNI peruano son 8 dígitos numéricos.
            if largo and (not numero.isdigit() or len(numero) != largo):
                raise serializers.ValidationError(
                    {
                        "numero_documento": (
                            f"El {tipo} debe tener {largo} dígitos numéricos."
                        )
                    }
                )
        return attrs


class HistoriaClinicaDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoriaClinicaDetalle
        fields = "__all__"


class DocumentoHistoriaClinicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentoHistoriaClinica
        fields = "__all__"

    def validate_archivo(self, value):
        return validar_archivo(value)


class OdontogramaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Odontograma
        fields = "__all__"


class AntecedentesPersonalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AntecedentesPersonales
        fields = "__all__"


class HistoriaClinicaSerializer(serializers.ModelSerializer):
    # Relaciones de solo lectura para inspeccionar la historia completa.
    documentos = DocumentoHistoriaClinicaSerializer(many=True, read_only=True)
    odontogramas = OdontogramaSerializer(many=True, read_only=True)
    antecedentes = AntecedentesPersonalesSerializer(read_only=True)

    class Meta:
        model = HistoriaClinica
        fields = "__all__"
