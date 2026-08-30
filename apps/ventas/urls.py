from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("ventas", views.VentaViewSet)
router.register("venta-servicios", views.VentaServicioViewSet)
router.register("descuentos", views.DescuentoViewSet)
router.register("adicionales", views.AdicionalViewSet)
router.register("cuotas", views.CuotaViewSet)
router.register("pagos", views.PagoViewSet)

urlpatterns = router.urls
