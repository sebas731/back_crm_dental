from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from shared.mixins import QueryParamFilterMixin

from .models import Adicional, Cuota, Descuento, Pago, Venta, VentaServicio
from .serializers import (
    AdicionalSerializer,
    CuotaSerializer,
    DescuentoSerializer,
    PagoSerializer,
    VentaSerializer,
    VentaServicioSerializer,
)


class VentaViewSet(QueryParamFilterMixin, viewsets.ModelViewSet):
    filterset_params = ["paciente", "estado", "tipo_pago"]
    queryset = Venta.objects.select_related("paciente").prefetch_related(
        "servicios", "descuentos", "adicionales", "cuotas__pagos"
    )
    serializer_class = VentaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["numero", "paciente__numero_documento"]
    ordering_fields = ["created_at", "total", "estado"]


class VentaServicioViewSet(QueryParamFilterMixin, viewsets.ModelViewSet):
    filterset_params = ["venta"]
    queryset = VentaServicio.objects.select_related("servicio")
    serializer_class = VentaServicioSerializer


class DescuentoViewSet(QueryParamFilterMixin, viewsets.ModelViewSet):
    filterset_params = ["venta"]
    queryset = Descuento.objects.all()
    serializer_class = DescuentoSerializer


class AdicionalViewSet(QueryParamFilterMixin, viewsets.ModelViewSet):
    filterset_params = ["venta"]
    queryset = Adicional.objects.all()
    serializer_class = AdicionalSerializer


class CuotaViewSet(QueryParamFilterMixin, viewsets.ModelViewSet):
    filterset_params = ["venta", "estado", "cita"]
    queryset = Cuota.objects.select_related("venta").prefetch_related("pagos")
    serializer_class = CuotaSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["numero", "fecha_limite"]


class PagoViewSet(QueryParamFilterMixin, viewsets.ModelViewSet):
    filterset_params = ["cuota", "metodo", "validado"]
    queryset = Pago.objects.select_related("cuota")
    serializer_class = PagoSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["fecha_pago", "monto"]

    @action(detail=True, methods=["post"])
    def validar(self, request, pk=None):
        """Valida el pago (lo marca como verificado por el usuario actual)."""
        pago = self.get_object()
        usuario = request.user if request.user.is_authenticated else None
        pago.validar(usuario=usuario, observacion=request.data.get("observacion", ""))
        return Response(self.get_serializer(pago).data)
