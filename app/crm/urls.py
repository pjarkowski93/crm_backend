from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register("sales", views.SaleViewSet, basename="sales")
router.register("clients", views.ClientViewSet, basename="clients")
router.register("roadmaps", views.RoadmapViewSet, basename="roadmaps")

urlpatterns = [
    path("", views.IndexView.as_view(), name="home"),
    path("charts/", views.ChartView.as_view(), name="chart"),
    path("charts2/", views.ChartView2.as_view(), name="chart2"),
    path("charts3/", views.ChartView3.as_view(), name="chart3"),
    path("upload/", views.UploadFile.as_view(), name="upload_files"),
    path("send_email/", views.SendPDFView.as_view(), name="send_email"),
    path(
        "import/",
        views.ImportExportSales.as_view(),
        name="import",
    ),
]
