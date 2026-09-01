from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("medicos", views.MedicoViewSet)
router.register("servicios", views.ServicioDentalViewSet)
router.register("horarios", views.HorarioAtencionViewSet)
router.register("citas", views.CitaViewSet)
router.register("atenciones", views.AtencionCitaViewSet)
router.register("notas-agenda", views.NotaAgendaViewSet)

urlpatterns = router.urls
