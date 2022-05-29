from datetime import datetime

import plotly.express as px
from django.db.models import F, Sum
from django.db.models.functions import ExtractMonth
from django.shortcuts import render
from django_filters import rest_framework as rest_filters
from rest_framework import permissions, viewsets
from rest_framework.views import APIView

from crm.forms import DateForm

from . import models, serializers


class SaleViewSet(viewsets.ModelViewSet):
    queryset = models.Sale.objects.all()
    serializer_class = serializers.SaleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [rest_filters.DjangoFilterBackend]
    lookup_field = "uuid"


class RoadmapViewSet(viewsets.ModelViewSet):
    queryset = models.Roadmap.objects.all()
    serializer_class = serializers.RoadmapSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [rest_filters.DjangoFilterBackend]
    lookup_field = "uuid"


class ClientViewSet(viewsets.ModelViewSet):
    queryset = models.Client.objects.all()
    serializer_class = serializers.ClientSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [rest_filters.DjangoFilterBackend]
    filterset_fields = [
        "name",
        "country",
        "address_line",
        "city",
        "email",
        "nip",
        "trader__email",
    ]
    ordering_fields = ["name"]
    lookup_field = "uuid"


class IndexView(APIView):
    def get(self, request, **kwargs):
        return render(request, "dashboard/index.html")


class ChartView(APIView):
    """
    List all snippets, or create a new snippet.
    """

    def get(self, request, **kwargs):
        sales = (
            models.Sale.objects.all()
            .values("brand", "client__name")
            .annotate(brand_amount=Sum("amount"))
            .annotate(
                brand_name=F("brand"),
                brand_amount=F("brand_amount"),
                client_name=F("client__name"),
            )
            .annotate()
        )
        fig = px.bar(
            sales,
            x="brand_name",
            y="brand_amount",
            color="client_name",
            barmode="group",
            title="Sum amount per brand and client",
            text="client_name",
            height=900,
        )
        fig.update_yaxes(automargin=True, dtick=100000)
        chart = fig.to_html()

        context = {"chart": chart}
        return render(request, "chart.html", context)


class ChartView2(APIView):
    def get(self, request, **kwargs):
        all_sales = (
            models.Sale.objects.all()
            .values("client__name")
            .annotate(client_amount=Sum("amount"))
            .annotate(name=F("client__name"), amount=F("client_amount"))
        )
        fig = px.bar(
            all_sales,
            x="name",
            y="amount",
            color="name",
            title="Sum amount per client",
            text_auto=".2s",
            height=900,
        )
        fig.update_yaxes(automargin=True, dtick=100000)
        chart = fig.to_html()

        context = {"chart": chart}
        return render(request, "chart2.html", context)


class ChartView3(APIView):
    MONTHS = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    }

    def get(self, request, **kwargs):
        all_sales_items = models.Sale.objects.all()
        if start_date := request.GET.get("start"):
            all_sales_items = all_sales_items.filter(created_date__gte=start_date)
        if end_date := request.GET.get("end"):
            all_sales_items = all_sales_items.filter(created_date__lte=end_date)

        all_sales = (
            all_sales_items.values("created_date")
            .annotate(client_amount=Sum("amount"))
            .annotate(sales_date=F("created_date"), amount=F("client_amount"))
            .annotate(sales_month=ExtractMonth("sales_date"))
            .values("sales_month", "amount")
        )
        to_return = []
        for sale in all_sales:
            to_return.append(
                {
                    "amount": sale["amount"],
                    "sales_month": self.MONTHS[sale["sales_month"]],
                    "to_sort": sale["sales_month"],
                }
            )

        fig = px.bar(
            sorted(to_return, key=lambda d: d["to_sort"]),
            x="sales_month",
            y="amount",
            color="sales_month",
            title="Sales per month",
            text_auto=".2s",
            height=800,
        )
        fig.update_yaxes(automargin=True, dtick=100000)
        chart = fig.to_html()

        context = {"chart": chart, "form": DateForm}
        return render(request, "chart3.html", context)
