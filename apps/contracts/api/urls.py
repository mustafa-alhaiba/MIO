from django.urls import path, include
from rest_framework.routers import DefaultRouter
 
from apps.contracts.api import views as contract_views

router = DefaultRouter()
router.register(r"contracts", contract_views.ContractViewSet, basename="contract")
 
urlpatterns = [
    path("", include(router.urls)),
]