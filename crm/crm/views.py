from django.shortcuts import render
from django_filters import rest_framework as rest_filters
from rest_framework import permissions, viewsets
from rest_framework.views import APIView

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


class ChartView(APIView):
    """
    List all snippets, or create a new snippet.
    """

    def get(self, request, format=None):
        import collections

        sales = models.Sale.objects.all().values("amount", "brand", "client__name")
        data = {}
        for sale in sales:
            if data.get(f'{sale["client__name"]} {sale["brand"].lower()}'):
                data[f'{sale["client__name"]} {sale["brand"].lower()}'] += float(
                    sale["amount"]
                )
            else:
                data[f'{sale["client__name"]} {sale["brand"].lower()}'] = float(
                    sale["amount"]
                )
            if data.get(f'{sale["client__name"].lower()} -- SUM'):
                data[f'{sale["client__name"].lower()} -- SUM'] += float(sale["amount"])
            else:
                data[f'{sale["client__name"].lower()} -- SUM'] = float(sale["amount"])

        # sales = models.Sale.objects.all().aggregate()

        my_dict = {
            "data": dict(collections.OrderedDict(sorted(data.items()))),
        }
        return render(request, "chart.html", context=my_dict)
