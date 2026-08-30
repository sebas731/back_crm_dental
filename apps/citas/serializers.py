from rest_framework import serializers

from .models import AtencionCita, Cita, HorarioAtencion, Medico, ServicioDental


class MedicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medico
        fields = "__all__"


class ServicioDentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicioDental
        fields = "__all__"


class HorarioAtencionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HorarioAtencion
        fields = "__all__"


class AtencionCitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AtencionCita
        fields = "__all__"


class CitaSerializer(serializers.ModelSerializer):
    atencion = AtencionCitaSerializer(read_only=True)

    class Meta:
        model = Cita
        fields = "__all__"
