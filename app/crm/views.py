import datetime
import os
from typing import Tuple

import pdfkit
import plotly.express as px
from crm.forms import ClientForm, DateForm, DateTimeForm, PDFForm
from crm.utils import EmailSender, ImportClient, ImportSales
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
from tablib import Dataset
from user.permissions import (
    ManagerPermissions,
    TeamleaderPermissions,
    TraderPermissions,
)

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


class ImportExportSales(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, **kwargs):
        return render(request, "crm/import.html")

    def post(self, request, *args, **kwargs):
        import_classes = {"sales": ImportSales, "client": ImportClient}
        dataset = Dataset()
        if not request.FILES.get("file_value"):
            messages.warning(request, "Plik nie został wybrany.")
            return redirect("import")
        if request.data.get("class_name") not in list(import_classes.keys()):
            messages.warning(request, "Proszę wybrać co chcesz zaimportować.")
            return redirect("import")

        new_sales = request.FILES["file_value"]
        if not new_sales.name.endswith("xlsx"):
            messages.warning(
                request, "Nieprawidłowy format pliku. Obsługiwany tylko xlsx."
            )
            return redirect("import")

        loaded_new_sales = dataset.load(new_sales.read(), format="xlsx")
        import_class = import_classes[request.data["class_name"]]()
        results = import_class.import_data(loaded_new_sales.dict)
        messages.success(request, "Wynik importu")
        return render(
            request,
            "crm/import.html",
            context={request.data["class_name"]: results},
        )


class ChartView(APIView):
    """
    List all snippets, or create a new snippet.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        empty_qs = models.Sale.objects.none()
        queryset = None
        if self.request.user.is_staff:
            queryset = models.Sale.objects.all()
            return queryset
        if (
            TraderPermissions.can_view_only_my_sales
            in self.request.user.get_group_permissions()
        ):
            if queryset:
                queryset = queryset.filter(client__trader=self.request.user)
            else:
                queryset = models.Sale.objects.filter(client__trader=self.request.user)
        if (
            TeamleaderPermissions.can_view_my_group_sales
            in self.request.user.get_group_permissions()
        ):
            if queryset:
                queryset = queryset.filter(client__trader__team=self.request.user.team)
            else:
                queryset = models.Sale.objects.filter(
                    client__trader__team=self.request.user.team
                )
        if (
            ManagerPermissions.can_view_department_sales
            in self.request.user.get_group_permissions()
        ):
            if queryset:
                queryset = queryset.filter(
                    client__trader__department=self.request.user.department
                )
            else:
                queryset = models.Sale.objects.filter(
                    client__trader__department=self.request.user.department
                )
        if not queryset:
            return empty_qs
        return queryset

    def get(self, request, **kwargs):
        sales = (
            self.get_queryset()
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
        return render(request, "crm/chart.html")


class ChartView2(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        empty_qs = models.Sale.objects.none()
        queryset = None
        if self.request.user.is_staff:
            queryset = models.Sale.objects.all()
            return queryset
        if (
            TraderPermissions.can_view_only_my_sales
            in self.request.user.get_group_permissions()
        ):
            if queryset:
                queryset = queryset.filter(client__trader=self.request.user)
            else:
                queryset = models.Sale.objects.filter(client__trader=self.request.user)
        if (
            TeamleaderPermissions.can_view_my_group_sales
            in self.request.user.get_group_permissions()
        ):
            if queryset:
                queryset = queryset.filter(client__trader__team=self.request.user.team)
            else:
                queryset = models.Sale.objects.filter(
                    client__trader__team=self.request.user.team
                )
        if (
            ManagerPermissions.can_view_department_sales
            in self.request.user.get_group_permissions()
        ):
            if queryset:
                queryset = queryset.filter(
                    client__trader__department=self.request.user.department
                )
            else:
                queryset = models.Sale.objects.filter(
                    client__trader__department=self.request.user.department
                )
        if not queryset:
            return empty_qs
        return queryset

    def get(self, request, **kwargs):
        all_sales = (
            self.get_queryset()
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
        return render(request, "crm/chart2.html")


class ChartView3(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        empty_qs = models.Sale.objects.none()
        queryset = None
        if self.request.user.is_staff:
            queryset = models.Sale.objects.all()
            return queryset
        if (
            TraderPermissions.can_view_only_my_sales
            in self.request.user.get_group_permissions()
        ):
            if queryset:
                queryset = queryset.filter(client__trader=self.request.user)
            else:
                queryset = models.Sale.objects.filter(client__trader=self.request.user)
        if (
            TeamleaderPermissions.can_view_my_group_sales
            in self.request.user.get_group_permissions()
        ):
            if queryset:
                queryset = queryset.filter(client__trader__team=self.request.user.team)
            else:
                queryset = models.Sale.objects.filter(
                    client__trader__team=self.request.user.team
                )
        if (
            ManagerPermissions.can_view_department_sales
            in self.request.user.get_group_permissions()
        ):
            if queryset:
                queryset = queryset.filter(
                    client__trader__department=self.request.user.department
                )
            else:
                queryset = models.Sale.objects.filter(
                    client__trader__department=self.request.user.department
                )
        if not queryset:
            return empty_qs
        return queryset

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
        all_sales_items = self.get_queryset()
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
        initial_data = {}
        client_initial = {}
        three_months = datetime.date.today() - relativedelta(months=+3)
        current_date = datetime.date.today().strftime("%Y-%m-%d")
        if start_date := self.request.data.get("start"):
            initial_data.update({"start": start_date})
        else:
            initial_data.update({"start": three_months})
        if end_date := self.request.data.get("end"):
            initial_data.update({"end": end_date})
        else:
            initial_data.update({"end": current_date})
        if client_name := request.GET.get("client"):
            client_initial.update({"client": client_name})
        date_form = DateForm(initial=initial_data)
        client_form = ClientForm(initial=client_initial)
        context = {
            "form": date_form,
            "select": client_form,
        }
        return render(request, "crm/chart3.html", context=context)


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

        messages.success(
            request, f"Plik został zapisany pod nazwą {file_name}.", extra_tags="alert"
        )
        context = {
            "chart": chart,
        }
        redirect_to = request.META["HTTP_REFERER"]
        return redirect(redirect_to, context=context)


class SendPDFView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        empty_qs = models.Files.objects.none()
        queryset = None
        if self.request.user.is_staff:
            queryset = models.Files.objects.all()
            return queryset
        if (
            TraderPermissions.can_view_only_my_sales
            in self.request.user.get_group_permissions()
        ):
            if queryset:
                queryset = queryset.filter(client__trader=self.request.user)
            else:
                queryset = models.Files.objects.filter(user=self.request.user)
        if (
            TeamleaderPermissions.can_view_my_group_sales
            in self.request.user.get_group_permissions()
        ):
            if queryset:
                queryset = queryset.filter(user__team=self.request.user.team)
            else:
                queryset = models.Files.objects.filter(
                    user__team=self.request.user.team
                )
        if (
            ManagerPermissions.can_view_department_sales
            in self.request.user.get_group_permissions()
        ):
            if queryset:
                queryset = queryset.filter(
                    user__department=self.request.user.department
                )
            else:
                queryset = models.Files.objects.filter(
                    user__department=self.request.user.department
                )
        if not queryset:
            return empty_qs
        return queryset

    def filter_queryset(self):
        date_to_filter = self.request.query_params.get("my_date_field")
        time_to_filter = self.request.query_params.get("my_time_field")
        current_date = datetime.date.today().strftime("%Y-%m-%d")
        current_datetime = datetime.datetime.now()
        current_time = current_datetime.time().strftime("%H:%M")
        if date_to_filter and time_to_filter:
            datetime_to_filter = datetime.datetime.strptime(
                f"{date_to_filter} {time_to_filter}", "%Y-%m-%d %H:%M"
            )
            return self.get_queryset().filter(created_datetime__gte=datetime_to_filter)
        if date_to_filter and not time_to_filter:
            datetime_to_filter = datetime.datetime.strptime(
                f"{date_to_filter} {current_time}", "%Y-%m-%d %H:%M"
            )
            return self.get_queryset().filter(created_datetime__gte=date_to_filter)
        if not date_to_filter and time_to_filter:
            datetime_to_filter = datetime.datetime.strptime(
                f"{current_date} {time_to_filter}", "%Y-%m-%d %H:%M"
            )
            return self.get_queryset().filter(created_datetime__gte=datetime_to_filter)
        return self.get_queryset()

    def get_initial_datetime_form(self):
        date_to_filter = self.request.query_params.get("my_date_field")
        time_to_filter = self.request.query_params.get("my_time_field")
        current_date = datetime.date.today().strftime("%Y-%m-%d")
        current_datetime = datetime.datetime.now()
        current_time = current_datetime.time().strftime("%H:%M")
        initial_data = {"my_date_field": current_date, "my_time_field": current_time}
        if date_to_filter and time_to_filter:
            initial_data["my_date_field"] = date_to_filter
            initial_data["my_time_field"] = time_to_filter
        if date_to_filter and not time_to_filter:
            initial_data["my_date_field"] = date_to_filter
        if not date_to_filter and time_to_filter:
            initial_data["my_time_field"] = time_to_filter
        return DateTimeForm(initial=initial_data)

    def get(self, request, **kwargs):
        form = PDFForm()
        datetime_form = self.get_initial_datetime_form()
        choices = []
        for file in self.filter_queryset().values("uuid", "file_name"):
            choices.append((str(file["uuid"]), file["file_name"]))

        form.fields["files"].choices = choices
        context = {"form": form, "datetime_form": datetime_form}
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
        messages.success(
            request,
            f"Email has been sent to {request_data['send_to']}.",
            extra_tags="alert",
        )
        initial_data = {
            "files": request_data.getlist("files"),
            "message": request_data.get("message"),
            "send_to": request_data.get("send_to"),
            "subject": request_data.get("subject"),
        }
        context = {"form": PDFForm(initial=initial_data)}
        return render(request, "crm/pdf_sender.html", context=context)
