from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RuleViewSet

router = DefaultRouter()
router.register(r'', RuleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]