from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("users", views.UserViewSet)
router.register("profiles", views.UserProfileViewSet)

urlpatterns = router.urls
