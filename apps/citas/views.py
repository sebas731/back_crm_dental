from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from shared.mixins import QueryParamFilterMixin
from shared.permissions import GestionAgenda, GestionClinica, SoloAdministrativos

from .models import (
    AtencionCita,
    Cita,
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
    queryset = Cita.objects.select_related(
        "paciente", "medico", "servicio"
    ).prefetch_related("atencion")
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
        """Al agendar una cita con servicio con precio, genera su venta."""
        cita = serializer.save()
        # Solo se genera venta si el servicio tiene un precio > 0; evita
        # ventas de S/ 0.00 que quedarían atascadas en "Pendiente".
        precio = cita.servicio.precio if cita.servicio_id else 0
        if precio and precio > 0:
            from apps.ventas.models import Venta, VentaServicio

            usuario = (
                self.request.user if self.request.user.is_authenticated else None
            )
            venta = Venta.objects.create(
                cita=cita,
                paciente=cita.paciente,
                tipo_pago=Venta.TipoPago.CONTADO,
                total=precio,
                registrado_por=usuario,
            )
            VentaServicio.objects.create(
                venta=venta,
                servicio=cita.servicio,
                cantidad=1,
                precio_unitario=precio,
            )

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

        # Sincroniza el estado de la cita.
        if data["estado"] == AtencionCita.Estado.ATENDIDO:
            cita.estado = Cita.Estado.ATENDIDA
        elif data["estado"] == AtencionCita.Estado.FALTO:
            cita.estado = Cita.Estado.NO_ASISTIO
        else:  # NO_PAGO
            cita.estado = Cita.Estado.CANCELADA
        cita.save(update_fields=["estado", "updated_at"])

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
    queryset = NotaAgenda.objects.select_related("autor")

    def get_queryset(self):
        qs = super().get_queryset()
        desde = self.request.query_params.get("desde")
        hasta = self.request.query_params.get("hasta")
        fecha = self.request.query_params.get("fecha")
        if fecha:
            qs = qs.filter(fecha=fecha)
        if desde:
            qs = qs.filter(fecha__gte=desde)
        if hasta:
            qs = qs.filter(fecha__lte=hasta)
        return qs

    def perform_create(self, serializer):
        usuario = self.request.user if self.request.user.is_authenticated else None
        serializer.save(autor=usuario)
