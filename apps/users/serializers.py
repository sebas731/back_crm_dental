from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from shared.permissions import ROLES_ADMINISTRATIVOS

from .models import UserProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(read_only=True)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "fullname",
            "rol",
            "is_active",
            "is_staff",
            "password",
        ]
        read_only_fields = ["is_staff"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo un administrativo puede asignar rol o (des)activar cuentas.
        # Para el resto, estos campos son de solo lectura: evita que un usuario
        # se autoascienda a ADMIN vía PATCH sobre su propia cuenta.
        request = self.context.get("request")
        rol = getattr(getattr(request, "user", None), "rol", None)
        if rol not in ROLES_ADMINISTRATIVOS:
            for campo in ("rol", "is_active"):
                if campo in self.fields:
                    self.fields[campo].read_only = True

    def validate_password(self, value):
        # Aplica los validadores de contraseña de Django (longitud, comunes…).
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"
