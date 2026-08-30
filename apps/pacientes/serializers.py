from rest_framework import serializers

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


class HistoriaClinicaDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoriaClinicaDetalle
        fields = "__all__"


class DocumentoHistoriaClinicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentoHistoriaClinica
        fields = "__all__"


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
