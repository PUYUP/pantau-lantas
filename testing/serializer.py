from django.contrib.auth.models import User
from django.db.models import Avg, Count, Min, Sum
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import routers, serializers, viewsets
from rest_framework.response import Response
from rest_framework.validators import UniqueTogetherValidator

# Import models
from .models import Kategori, Buku

# Create serializers
class KategoriSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kategori
        fields = "__all__"

class BukuSerializer(serializers.ModelSerializer):
    kategori = KategoriSerializer(many=True)

    class Meta:
        model = Buku
        fields = "__all__"

    def create(self, validated_data):
        kategori_data = validated_data.pop("kategori")
        
