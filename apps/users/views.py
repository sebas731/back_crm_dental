from django.contrib.auth import get_user_model
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from shared.permissions import (
    ROLES_ADMINISTRATIVOS,
    GestionUsuarios,
    SoloAdministrativos,
)

from .models import UserProfile
from .serializers import UserProfileSerializer, UserSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [GestionUsuarios]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["username", "date_joined"]

    def get_queryset(self):
        qs = User.objects.all().order_by("username")
        # Un usuario no administrativo solo se ve a sí mismo.
        if getattr(self.request.user, "rol", None) not in ROLES_ADMINISTRATIVOS:
            return qs.filter(pk=self.request.user.pk)
        return qs

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Datos del usuario autenticado."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.select_related("user")
    serializer_class = UserProfileSerializer
    permission_classes = [SoloAdministrativos]
