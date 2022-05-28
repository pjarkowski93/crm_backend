from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register("sales", views.SaleViewSet, basename="sales")
router.register("clients", views.ClientViewSet, basename="clients")
router.register("roadmaps", views.RoadmapViewSet, basename="roadmaps")

urlpatterns = [
    path("", include(router.urls)),
    path("charts/", views.ChartView.as_view()),
]
