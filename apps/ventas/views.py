from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from shared.mixins import QueryParamFilterMixin
from shared.permissions import PuedeGestionarPagos

from .models import Adicional, Cuota, Descuento, Pago, Venta, VentaServicio
from .serializers import (
    AdicionalSerializer,
    CuotaSerializer,
    DescuentoSerializer,
    PagoSerializer,
    VentaSerializer,
    VentaServicioSerializer,
)

VENTA_BLOQUEADA = (
    "La venta está bloqueada (tiene pagos validados o está anulada) y no se "
    "pueden modificar sus servicios, adicionales ni descuentos. Duplicá la "
    "venta para corregirla y anulá la original."
)


class VentaViewSet(QueryParamFilterMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, PuedeGestionarPagos]
    filterset_params = ["paciente", "estado", "tipo_pago"]
    queryset = Venta.objects.select_related("paciente").prefetch_related(
        "servicios", "descuentos", "adicionales", "cuotas__pagos"
    )
    serializer_class = VentaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["numero", "paciente__numero_documento"]
    ordering_fields = ["created_at", "total", "estado"]

    @action(detail=True, methods=["post"])
    def anular(self, request, pk=None):
        """Anula la venta (devoluciones / errores). Conserva su historial."""
        venta = self.get_object()
        if venta.estado == Venta.Estado.ANULADO:
            raise ValidationError("La venta ya está anulada.")
        venta.anular(motivo=request.data.get("motivo", ""))
        return Response(self.get_serializer(venta).data)

    @action(detail=True, methods=["post"])
    def duplicar(self, request, pk=None):
        """Crea una copia editable (nueva venta) sin pagos, para corregir."""
        original = self.get_object()
        usuario = request.user if request.user.is_authenticated else None
        nueva = original.duplicar(usuario=usuario)
        serializer = self.get_serializer(nueva)
        return Response(serializer.data, status=201)


class RecalculaVentaMixin:
    """Recalcula el total de la venta cuando cambian sus líneas.

    Bloquea la edición si la venta está congelada (pagos validados / anulada).
    """

    def _verificar_editable(self, venta):
        if venta and not venta.editable:
            raise ValidationError(VENTA_BLOQUEADA)

    def perform_create(self, serializer):
        self._verificar_editable(serializer.validated_data.get("venta"))
        obj = serializer.save()
        obj.venta.recalcular_total()

    def perform_update(self, serializer):
        self._verificar_editable(serializer.instance.venta)
        obj = serializer.save()
        obj.venta.recalcular_total()

    def perform_destroy(self, instance):
        self._verificar_editable(instance.venta)
        venta = instance.venta
        instance.delete()
        venta.recalcular_total()


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
    queryset = Cuota.objects.select_related("venta").prefetch_related("pagos")
    serializer_class = CuotaSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["numero", "fecha_limite"]

    def perform_create(self, serializer):
        venta = serializer.validated_data.get("venta")
        if venta and not venta.editable:
            raise ValidationError(VENTA_BLOQUEADA)
        serializer.save()

    def perform_update(self, serializer):
        cuota = serializer.instance
        nuevo_monto = serializer.validated_data.get("monto")
        # No se puede cambiar el monto de una cuota que ya tiene pagos.
        if (
            nuevo_monto is not None
            and nuevo_monto != cuota.monto
            and cuota.pagos.exists()
        ):
            raise ValidationError(
                "No se puede cambiar el monto de una cuota que ya tiene pagos."
            )
        serializer.save()

    def perform_destroy(self, instance):
        # Borrar la cuota arrastraría sus pagos (cascade). No permitido.
        if instance.pagos.exists():
            raise ValidationError(
                "No se puede eliminar una cuota que ya tiene pagos "
                "registrados. Anulá la venta si necesitás revertirla."
            )
        instance.delete()


class PagoViewSet(QueryParamFilterMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, PuedeGestionarPagos]
    filterset_params = ["cuota", "metodo", "validado"]
    queryset = Pago.objects.select_related("cuota")
    serializer_class = PagoSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["fecha_pago", "monto"]

    def perform_create(self, serializer):
        cuota = serializer.validated_data.get("cuota")
        if cuota and cuota.venta.estado == Venta.Estado.ANULADO:
            raise ValidationError(
                "No se pueden registrar pagos en una venta anulada."
            )
        # Flujo de un solo paso: el pago queda confirmado al registrarse
        # (no hay un paso aparte de "validar").
        from django.utils import timezone

        usuario = self.request.user if self.request.user.is_authenticated else None
        serializer.save(
            validado=True,
            validado_por=usuario,
            fecha_validacion=timezone.now(),
        )

    def perform_update(self, serializer):
        if serializer.instance.validado:
            raise ValidationError(
                "Un pago validado no se puede modificar. Anulá la venta si "
                "necesitás corregirlo."
            )
        serializer.save()

    def perform_destroy(self, instance):
        if instance.validado:
            raise ValidationError(
                "Un pago validado no se puede eliminar. Anulá la venta si "
                "necesitás revertirlo."
            )
        instance.delete()

    @action(detail=True, methods=["post"])
    def validar(self, request, pk=None):
        """Valida el pago (lo marca como verificado por el usuario actual)."""
        pago = self.get_object()
        # Idempotente: si ya está validado, no se reescribe quién/cuándo.
        if pago.validado:
            return Response(self.get_serializer(pago).data)
        usuario = request.user if request.user.is_authenticated else None
        pago.validar(usuario=usuario, observacion=request.data.get("observacion", ""))
        return Response(self.get_serializer(pago).data)
