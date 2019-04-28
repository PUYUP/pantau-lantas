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

from rest_framework.settings import api_settings
from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FileUploadParser

# Import models
from reports.models import PoliceNumber, Reported, Vehicle
from users.models import UserPoliceNumber, UserPoliceNumberClaim
from mains.models import FileManagement, FileManagementType

# Restful
from reports.serializer import PoliceNumberSerializer, ReportedSerializer
from mains.serializer import FileManagementSerializer, FileManagementTypeSerializer

# Create a forms
class ReportedForm(forms.ModelForm):
	"""
	Form kirim laporan
	"""
	vehicle = forms.ModelChoiceField(
		queryset=Vehicle.objects.all(),
		label="Jenis Kendaraan",
		widget=forms.Select
	)
	police_number = forms.CharField(
		max_length=255,
		label="Nomor Polisi / Plat"
	)

	class Meta:
		model = Reported
		fields = ["violation", "police_number", "vehicle", "explanation", "location", "picture"]
		labels = {
			"violation": "Pelanggaran",
			"explanation": "Keterangan Pelanggaran",
			"location": "Lokasi",
			"picture": "Foto",
		}


# Create your views here.
class HomeView(View):
	"""
	Halaman beranda
	"""
	template_name = "home.html"
	form = ReportedForm()
	context = {
		"form": form
	}

	# Aksi GET
	def get(self, request):
		police_number_list = PoliceNumber.objects.annotate(num_reported=Count("reported"))
		reported_list = Reported.objects.annotate(num_reported=Count("police_number"))

		self.context["police_number"] = police_number_list
		self.context["police_number_reported"] = police_number_list[0].num_reported
		self.context["reported"] = reported_list;
		self.context["settings_auth"] = api_settings.DEFAULT_AUTHENTICATION_CLASSES
		return render(request, self.template_name, self.context)

	# Aksi POST
	def post(self, request, *agrs, **kwargs):
		return render(request, self.template_name, self.context)


class FileManagementView(APIView):
	parser_class = (FileUploadParser,)

	def post(self, request, format="json", *agrs, **kwargs):
		context = {
			"request": self.request
		}

		if request.user.is_authenticated:
			serializer = FileManagementSerializer(data=request.data, context=context)

			if serializer.is_valid(raise_exception=True):
				serializer.save()
				return Response(serializer.data, status=status.HTTP_201_CREATED)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		return Response({"errors": "Login required!"}, status=status.HTTP_401_UNAUTHORIZED)


class FileManagementDetailView(APIView):
	"""
	Detail per file
	"""
	@transaction.atomic
	def delete(self, request, pk, format="json"):
		if request.user.is_authenticated:
			user = self.request.user

			try:
				file = FileManagement.objects.get(pk=pk, uploader=user)
			except FileManagement.DoesNotExist:
				file = None

			uploader_is_self = True if request.user.username == file.uploader.username else False
			if file and uploader_is_self:
				file.delete()
				return Response(status=status.HTTP_204_NO_CONTENT)
			return Response(status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
		return Response({"errors": "Login required!"}, status=status.HTTP_401_UNAUTHORIZED)


class FileManagementTypeView(APIView):
	"""
	Listing semua jenis file/dokumen
	"""
	# Settings
	permission_classes = (AllowAny,)

	def get(self, request, format="json"):
		vehicle = FileManagementType.objects.all()
		serializer = FileManagementTypeSerializer(vehicle, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)
