from crm.models import Client, Roadmap, Sale
from rest_framework import serializers


class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        exclude = ("id",)


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        exclude = ("id",)


class RoadmapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roadmap
        exclude = ("id",)
