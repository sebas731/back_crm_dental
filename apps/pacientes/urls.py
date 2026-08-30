from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("clientes", views.ClienteViewSet)
router.register("pacientes", views.PacienteViewSet)
router.register("acompanantes", views.AcompananteViewSet)
router.register("historias-clinicas", views.HistoriaClinicaViewSet)
router.register("historias-clinicas-detalle", views.HistoriaClinicaDetalleViewSet)
router.register("documentos", views.DocumentoHistoriaClinicaViewSet)
router.register("odontogramas", views.OdontogramaViewSet)
router.register("antecedentes", views.AntecedentesPersonalesViewSet)

urlpatterns = router.urls
