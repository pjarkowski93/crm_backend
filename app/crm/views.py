import datetime
import os
from typing import Tuple

import pdfkit
import plotly.express as px
from crm.forms import ClientForm, DateForm, PDFForm
from crm.utils import EmailSender
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import F, QuerySet, Sum
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django_filters import rest_framework as rest_filters
from rest_framework import permissions, viewsets
from rest_framework.views import APIView

from . import models, serializers

User = get_user_model()


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
        return render(request, "crm/dashboard.html")


class ChartView(APIView):
    """
    List all snippets, or create a new snippet.
    """

    permission_classes = [permissions.IsAuthenticated]

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
        if sales:
            fig = px.bar(
                sales,
                x="brand_name",
                y="brand_amount",
                color="client_name",
                barmode="group",
                title="Suma sprzedaży marka-klient",
                text="client_name",
                height=900,
            )
            fig.update_yaxes(automargin=True, dtick=100000)
            chart = fig.to_html()

            context = {"chart": chart}
            return render(request, "crm/chart.html", context)
        messages.warning(request, "Brak danych dla podanych filtrów.")
        return redirect("home")


class ChartView2(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, **kwargs):
        all_sales = (
            models.Sale.objects.all()
            .values("client__name")
            .annotate(client_amount=Sum("amount"))
            .annotate(name=F("client__name"), amount=F("client_amount"))
        )
        if all_sales:
            fig = px.bar(
                all_sales,
                x="name",
                y="amount",
                color="name",
                title="Suma sprzedaży dla każdego klienta",
                text_auto=".2s",
                height=900,
            )
            fig.update_yaxes(automargin=True, dtick=100000)
            chart = fig.to_html()

            context = {"chart": chart}
            return render(request, "crm/chart2.html", context)
        messages.warning(request, "Brak danych dla podanych filtrów.")
        return redirect("home")


class ChartView3(APIView):
    permission_classes = [permissions.IsAuthenticated]
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
    REVERSE_MONTHS = {
        month_name: month_value for month_value, month_name in MONTHS.items()
    }

    def filter_data(
        self, request, qs: QuerySet
    ) -> Tuple[QuerySet, Tuple[str, str, str]]:
        three_months = datetime.date.today() - relativedelta(months=+3)
        current_date = datetime.date.today().strftime("%Y-%m-%d")
        if start_date := request.GET.get("start"):
            qs = qs.filter(sale_date_from__isnull=False, sale_date_from__gte=start_date)
        else:
            qs = qs.filter(
                sale_date_from__isnull=False, sale_date_from__gte=three_months
            )
        if end_date := request.GET.get("end"):
            qs = qs.filter(sale_date_from__isnull=False, sale_date_from__lte=end_date)
        else:
            qs = qs.filter(
                sale_date_from__isnull=False, sale_date_from__lte=current_date
            )
        if client_name := request.GET.get("client"):
            if not client_name == "all":
                qs = qs.filter(client__name=client_name)
        months_to_filter = []
        for sale_obj in qs:
            months_to_filter.append(self.MONTHS[sale_obj.sale_date_from.month])

        sales_month = models.SaleMonths.objects.filter(
            sale__in=qs, sale_month__in=months_to_filter
        )

        if not start_date:
            start_date = three_months
        if not end_date:
            end_date = current_date

        return (
            sales_month.annotate(client_amount=Sum("sale_month_amount"))
            .annotate(amount=F("client_amount"), sales_month=F("sale_month"))
            .values("sales_month", "amount"),
            (start_date, end_date, client_name),
        )

    def get(self, request, **kwargs):
        all_sales_items = models.Sale.objects.all()
        filtered_sales, data = self.filter_data(request, all_sales_items)
        start_date, end_date, client_name = data
        if filtered_sales:
            to_return = []
            for sale in filtered_sales:
                to_return.append(
                    {
                        "amount": sale["amount"],
                        "sales_month": sale["sales_month"],
                        "to_sort": self.REVERSE_MONTHS[sale["sales_month"]],
                    }
                )
            last_value_choose_value = client_name if client_name else "all"
            client_form = ClientForm(initial={"client": last_value_choose_value})
            last_date_form_data = {}
            if start_date and end_date:
                last_date_form_data = {"start": start_date, "end": end_date}
            elif start_date and not end_date:
                last_date_form_data = {
                    "start": start_date,
                }
            elif not start_date and end_date:
                last_date_form_data = {"end": end_date}
            date_form = DateForm(initial=last_date_form_data)
            if not to_return:
                return render(
                    request,
                    "chart3.html",
                    context={
                        "message": "Brak danych dla podanych filtrów.",
                        "form": date_form,
                        "select": client_form,
                    },
                )
            fig = px.bar(
                sorted(to_return, key=lambda d: d["to_sort"]),
                x="sales_month",
                y="amount",
                color="sales_month",
                title="Miesięczna sprzedaż",
                text_auto=".2s",
                height=800,
            )
            fig.update_yaxes(automargin=True, dtick=100000)
            chart = fig.to_html()

            context = {
                "chart": chart,
                "form": date_form,
                "select": client_form,
            }
            return render(request, "crm/chart3.html", context)
        messages.warning(
            request, "Brak danych dla podanych filtrów.", extra_tags="alert"
        )
        return redirect("home")


class UploadFile(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file_name = request.POST["file_name"]
        chart = request.POST["chart"]
        if len(file_name) > 4:
            if file_name[-4] != ".pdf":
                file_name = f"{file_name}.pdf"
            else:
                file_name = f"{file_name}.pdf"
        else:
            file_name = f"{file_name}.pdf"
        path_to_save = os.path.join(settings.MEDIA_ROOT, file_name)
        if pdfkit.from_string(chart, path_to_save):
            if models.Files.objects.filter(path_to_file=path_to_save).exists():
                return HttpResponse(status=400, content={"file_name": "Already exists"})
            my_user = User.objects.all().first()
            models.Files.objects.create(
                user=my_user, file_name=file_name, path_to_file=path_to_save
            )
        else:
            return HttpResponse(status=400)

        return redirect("home")


class SendPDFView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, **kwargs):
        context = {"form": PDFForm(), "files": models.Files.objects.all()}
        return render(request, "crm/pdf_sender.html", context=context)

    def post(self, request, *args, **kwargs):
        request_data = request.data
        files_to_send = models.Files.objects.filter(
            uuid__in=request_data.getlist("files")
        )
        sender = EmailSender()
        sender.send(
            recipient=request_data["send_to"],
            message=request_data["message"],
            subject=request_data["subject"],
            files=files_to_send,
        )
        context = {
            "form": PDFForm(initial=request_data),
            "message": f"Email has been sent to {request_data['send_to']}.",
        }
        return render(request, "crm/pdf_sender.html", context=context)
