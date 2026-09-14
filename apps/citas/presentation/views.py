from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from shared.mixins import QueryParamFilterMixin
from shared.permissions import GestionAgenda, GestionClinica, SoloAdministrativos

from ..application import selectors, services
from ..models import (
    AtencionCita,
    HorarioAtencion,
    Medico,
    NotaAgenda,
    ServicioDental,
)
from .serializers import (
    AtencionCitaSerializer,
    CitaSerializer,
    HorarioAtencionSerializer,
    MedicoSerializer,
    NotaAgendaSerializer,
    ServicioDentalSerializer,
)


class MedicoViewSet(viewsets.ModelViewSet):
    permission_classes = [SoloAdministrativos]
    queryset = Medico.objects.all()
    serializer_class = MedicoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombres", "apellidos", "especialidad", "colegiatura"]
    ordering_fields = ["apellidos", "nombres", "created_at"]


class ServicioDentalViewSet(viewsets.ModelViewSet):
    permission_classes = [SoloAdministrativos]
    queryset = ServicioDental.objects.all()
    serializer_class = ServicioDentalSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre", "descripcion"]
    ordering_fields = ["nombre", "precio", "created_at"]


class HorarioAtencionViewSet(viewsets.ModelViewSet):
    permission_classes = [SoloAdministrativos]
    queryset = HorarioAtencion.objects.select_related("medico")
    serializer_class = HorarioAtencionSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["dia_semana", "hora_inicio"]


class CitaViewSet(QueryParamFilterMixin, viewsets.ModelViewSet):
    filterset_params = ["paciente", "medico", "estado", "servicio", "fecha"]
    queryset = selectors.cita_list()
    serializer_class = CitaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["motivo", "paciente__numero_documento"]
    ordering_fields = ["fecha", "hora_inicio", "estado", "created_at"]

    def get_permissions(self):
        # El médico solo consulta y atiende; crear/editar/borrar citas es
        # de roles clínicos (admin/manager/asistente).
        if self.action == "atender":
            return [IsAuthenticated()]
        return [GestionClinica()]

    def perform_create(self, serializer):
        # Al agendar una cita con servicio se genera su orden de venta.
        cita = serializer.save()
        services.cita_generar_orden(cita=cita, usuario=self.request.user)

    @action(detail=True, methods=["post"])
    def atender(self, request, pk=None):
        """
        Registra la atención (detalle) de la cita y actualiza su estado.
        Body: { estado, descripcion, evolucion, medico_atendio, firma }
        """
        cita = self.get_object()
        data = {
            "cita": cita.pk,
            "fecha_cita": request.data.get("fecha_cita", cita.fecha),
            "estado": request.data.get("estado", AtencionCita.Estado.ATENDIDO),
            "descripcion": request.data.get("descripcion", ""),
            "evolucion": request.data.get("evolucion", ""),
            "medico_atendio": request.data.get("medico_atendio", cita.medico_id),
            "firma": request.data.get("firma", ""),
        }
        atencion = getattr(cita, "atencion", None)
        serializer = AtencionCitaSerializer(atencion, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        services.cita_aplicar_atencion(cita=cita, estado_atencion=data["estado"])

        fresh = self.get_queryset().get(pk=cita.pk)
        return Response(
            self.get_serializer(fresh).data, status=status.HTTP_200_OK
        )


class AtencionCitaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = AtencionCita.objects.select_related("cita", "medico_atendio")
    serializer_class = AtencionCitaSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["fecha_cita", "created_at"]


class NotaAgendaViewSet(viewsets.ModelViewSet):
    permission_classes = [GestionAgenda]
    serializer_class = NotaAgendaSerializer
    # Atributo base para que el router infiera el basename; get_queryset aplica
    # el filtro real por fecha/rango.
    queryset = NotaAgenda.objects.all()

    def get_queryset(self):
        params = self.request.query_params
        return selectors.nota_list(
            fecha=params.get("fecha"),
            desde=params.get("desde"),
            hasta=params.get("hasta"),
        )

    def perform_create(self, serializer):
        usuario = self.request.user if self.request.user.is_authenticated else None
        serializer.save(autor=usuario)
