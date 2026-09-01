from rest_framework import serializers

from .models import (
    AtencionCita,
    Cita,
    HorarioAtencion,
    Medico,
    NotaAgenda,
    ServicioDental,
)


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

    # Estados que ya no ocupan la agenda (no cuentan para el solape).
    _ESTADOS_LIBERAN = {Cita.Estado.CANCELADA, Cita.Estado.NO_ASISTIO}

    def _campo(self, attrs, nombre):
        """Valor efectivo de un campo (el nuevo o el ya guardado)."""
        if nombre in attrs:
            return attrs[nombre]
        return getattr(self.instance, nombre, None)

    def validate(self, attrs):
        estado = self._campo(attrs, "estado") or Cita.Estado.PROGRAMADA

        # 1) No se puede marcar ATENDIDA a mano: debe hacerse vía "Atender"
        #    para que se registre la nota clínica (AtencionCita).
        tiene_atencion = bool(getattr(self.instance, "atencion", None))
        if estado == Cita.Estado.ATENDIDA and not tiene_atencion:
            raise serializers.ValidationError(
                "Para marcar la cita como Atendida usá la acción “Atender” "
                "y registrá la atención clínica."
            )

        # 2) Sin doble reserva: mismo médico, misma fecha y horario que choca.
        medico = self._campo(attrs, "medico")
        fecha = self._campo(attrs, "fecha")
        inicio = self._campo(attrs, "hora_inicio")
        fin = self._campo(attrs, "hora_fin")
        if medico and fecha and inicio and estado not in self._ESTADOS_LIBERAN:
            otras = Cita.objects.filter(medico=medico, fecha=fecha).exclude(
                estado__in=self._ESTADOS_LIBERAN
            )
            if self.instance:
                otras = otras.exclude(pk=self.instance.pk)
            for c in otras:
                c_fin = c.hora_fin or c.hora_inicio
                nueva_fin = fin or inicio
                # Solape de intervalos, o mismo inicio exacto (citas sin
                # duración definida ocupan igualmente ese horario).
                solapa = (inicio < c_fin and c.hora_inicio < nueva_fin) or (
                    inicio == c.hora_inicio
                )
                if solapa:
                    raise serializers.ValidationError(
                        "El médico ya tiene una cita que se cruza con ese "
                        f"horario ({c.hora_inicio.strftime('%H:%M')})."
                    )
        return attrs


class NotaAgendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotaAgenda
        fields = "__all__"
        read_only_fields = ["autor"]
