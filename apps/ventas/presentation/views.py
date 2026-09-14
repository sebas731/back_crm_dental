from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from shared.mixins import QueryParamFilterMixin
from shared.permissions import PuedeGestionarPagos

from ..application import selectors, services
from ..models import Adicional, Descuento, VentaServicio
from .serializers import (
    AdicionalSerializer,
    CuotaSerializer,
    DescuentoSerializer,
    PagoSerializer,
    VentaSerializer,
    VentaServicioSerializer,
)


class VentaViewSet(QueryParamFilterMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, PuedeGestionarPagos]
    filterset_params = ["paciente", "estado", "tipo_pago"]
    queryset = selectors.venta_list()
    serializer_class = VentaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["numero", "paciente__numero_documento"]
    ordering_fields = ["created_at", "total", "estado"]

    @action(detail=True, methods=["post"])
    def anular(self, request, pk=None):
        """Anula la venta (devoluciones / errores). Conserva su historial."""
        venta = services.venta_anular(
            venta=self.get_object(), motivo=request.data.get("motivo", "")
        )
        return Response(self.get_serializer(venta).data)

    @action(detail=True, methods=["post"])
    def duplicar(self, request, pk=None):
        """Crea una copia editable (nueva venta) sin pagos, para corregir."""
        nueva = services.venta_duplicar(
            original=self.get_object(), usuario=request.user
        )
        return Response(self.get_serializer(nueva).data, status=201)


class RecalculaVentaMixin:
    """Recalcula el total de la venta cuando cambian sus líneas.

    Bloquea la edición si la venta está congelada (pagos validados / anulada).
    """

    def perform_create(self, serializer):
        services.venta_verificar_editable(serializer.validated_data.get("venta"))
        obj = serializer.save()
        services.venta_recalcular(obj.venta)

    def perform_update(self, serializer):
        services.venta_verificar_editable(serializer.instance.venta)
        obj = serializer.save()
        services.venta_recalcular(obj.venta)

    def perform_destroy(self, instance):
        services.venta_verificar_editable(instance.venta)
        venta = instance.venta
        instance.delete()
        services.venta_recalcular(venta)


class VentaServicioViewSet(
    RecalculaVentaMixin, QueryParamFilterMixin, viewsets.ModelViewSet
):
    filterset_params = ["venta"]
    queryset = VentaServicio.objects.select_related("servicio")
    serializer_class = VentaServicioSerializer


class DescuentoViewSet(
    RecalculaVentaMixin, QueryParamFilterMixin, viewsets.ModelViewSet
):
    filterset_params = ["venta"]
    queryset = Descuento.objects.all()
    serializer_class = DescuentoSerializer


class AdicionalViewSet(
    RecalculaVentaMixin, QueryParamFilterMixin, viewsets.ModelViewSet
):
    filterset_params = ["venta"]
    queryset = Adicional.objects.all()
    serializer_class = AdicionalSerializer


class CuotaViewSet(QueryParamFilterMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, PuedeGestionarPagos]
    filterset_params = ["venta", "estado", "cita"]
    queryset = selectors.cuota_list()
    serializer_class = CuotaSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["numero", "fecha_limite"]

    def perform_create(self, serializer):
        services.cuota_verificar_creacion(serializer.validated_data.get("venta"))
        serializer.save()

    def perform_update(self, serializer):
        services.cuota_verificar_cambio_monto(
            cuota=serializer.instance,
            nuevo_monto=serializer.validated_data.get("monto"),
        )
        serializer.save()

    def perform_destroy(self, instance):
        services.cuota_verificar_eliminacion(instance)
        instance.delete()


class PagoViewSet(QueryParamFilterMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, PuedeGestionarPagos]
    filterset_params = ["cuota", "metodo", "validado"]
    queryset = selectors.pago_list()
    serializer_class = PagoSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["fecha_pago", "monto"]

    def perform_create(self, serializer):
        services.pago_verificar_registrable(serializer.validated_data.get("cuota"))
        serializer.save(**services.pago_campos_registro(self.request.user))

    def perform_update(self, serializer):
        services.pago_verificar_mutable(serializer.instance)
        serializer.save()

    def perform_destroy(self, instance):
        services.pago_verificar_mutable(instance)
        instance.delete()

    @action(detail=True, methods=["post"])
    def validar(self, request, pk=None):
        """Valida el pago (lo marca como verificado por el usuario actual)."""
        pago = services.pago_validar(
            pago=self.get_object(),
            usuario=request.user,
            observacion=request.data.get("observacion", ""),
        )
        return Response(self.get_serializer(pago).data)
