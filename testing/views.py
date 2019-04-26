from django.shortcuts import render
from django.db.models import Avg, Count, Min, Sum
from django.db import transaction
from django.views import View
from django import forms
from django.forms import ModelForm
from django.http import Http404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from users.serializer import UserSerializer
from testing.serializer import BukuSerializer
from testing.models import Model

# Create your views here.
class BukuView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format="JSON"):
        buku = Buku.objects.all()
        serializer = BukuSerializer(buku, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *agrs, **kwargs):
        
