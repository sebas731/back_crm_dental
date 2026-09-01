from rest_framework import filters, viewsets

from shared.mixins import QueryParamFilterMixin
from shared.permissions import GestionClinica

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
from .serializers import (
    AcompananteSerializer,
    AntecedentesPersonalesSerializer,
    ClienteSerializer,
    DocumentoHistoriaClinicaSerializer,
    HistoriaClinicaDetalleSerializer,
    HistoriaClinicaSerializer,
    OdontogramaSerializer,
    PacienteSerializer,
)


class ClienteViewSet(viewsets.ModelViewSet):
    permission_classes = [GestionClinica]
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre", "apellido", "segundo_apellido", "correo", "numero"]
    ordering_fields = ["nombre", "apellido", "created_at"]


class PacienteViewSet(viewsets.ModelViewSet):
    permission_classes = [GestionClinica]
    queryset = Paciente.objects.all().prefetch_related("acompanantes")
    serializer_class = PacienteSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "nombres",
        "apellido_paterno",
        "apellido_materno",
        "numero_documento",
    ]
    ordering_fields = ["apellido_paterno", "nombres", "created_at"]


class AcompananteViewSet(viewsets.ModelViewSet):
    permission_classes = [GestionClinica]
    queryset = Acompanante.objects.all()
    serializer_class = AcompananteSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre", "apellido_paterno", "apellido_materno", "dni"]


class HistoriaClinicaViewSet(QueryParamFilterMixin, viewsets.ModelViewSet):
    permission_classes = [GestionClinica]
    filterset_params = ["paciente"]
    queryset = HistoriaClinica.objects.all().prefetch_related(
        "documentos", "odontogramas"
    )
    serializer_class = HistoriaClinicaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["numero", "paciente__numero_documento"]
    ordering_fields = ["numero", "fecha_apertura", "created_at"]


class HistoriaClinicaDetalleViewSet(viewsets.ModelViewSet):
    permission_classes = [GestionClinica]
    queryset = HistoriaClinicaDetalle.objects.all()
    serializer_class = HistoriaClinicaDetalleSerializer


class DocumentoHistoriaClinicaViewSet(QueryParamFilterMixin, viewsets.ModelViewSet):
    permission_classes = [GestionClinica]
    filterset_params = ["historia_clinica", "tipo"]
    queryset = DocumentoHistoriaClinica.objects.all()
    serializer_class = DocumentoHistoriaClinicaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["titulo", "tipo"]


class OdontogramaViewSet(QueryParamFilterMixin, viewsets.ModelViewSet):
    permission_classes = [GestionClinica]
    filterset_params = ["historia_clinica"]
    queryset = Odontograma.objects.all()
    serializer_class = OdontogramaSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["fecha", "created_at"]


class AntecedentesPersonalesViewSet(QueryParamFilterMixin, viewsets.ModelViewSet):
    permission_classes = [GestionClinica]
    filterset_params = ["historia_clinica"]
    queryset = AntecedentesPersonales.objects.all()
    serializer_class = AntecedentesPersonalesSerializer
