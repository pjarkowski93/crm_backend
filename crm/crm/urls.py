from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register("sales", views.SaleViewSet, basename="sales")
router.register("clients", views.ClientViewSet, basename="clients")
router.register("roadmaps", views.RoadmapViewSet, basename="roadmaps")

urlpatterns = [
    path("home/", views.IndexView.as_view(), name="home"),
    path("charts/", views.ChartView.as_view(), name="chart"),
    path("charts2/", views.ChartView2.as_view(), name="chart2"),
    path("charts3/", views.ChartView3.as_view(), name="chart3"),
]
