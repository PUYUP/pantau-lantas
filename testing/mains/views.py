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

# Import models
from reports.models import PoliceNumber, Reported, Vehicle

# Restful
from reports.serializer import PoliceNumberSerializer, ReportedSerializer

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
		reporter = User.objects.get(pk=1)
		vehicle = Vehicle.objects.get(pk=1)
		police_number_init = "BH3904EF"
		police_number, created = PoliceNumber.objects.get_or_create(reporter=reporter, vehicle=vehicle, number=police_number_init)
		
		police_number_list = PoliceNumber.objects.annotate(num_reported=Count("reported"))
		reported_list = Reported.objects.annotate(num_reported=Count("police_number"))
		
		data = {
			"username": "foobar",
			"email": "foobar@google.com",
			"password": "123456",
		}
		
		self.context["data"] = data["username"]
		self.context["vehicle"] = vehicle
		self.context["police_number_init"] = police_number
		self.context["created"] = created
		self.context["police_number"] = police_number_list
		self.context["police_number_reported"] = police_number_list[0].num_reported
		self.context["reported"] = reported_list;
		return render(request, self.template_name, self.context)
	
	# Aksi POST
	def post(self, request, *agrs, **kwargs):
		return render(request, self.template_name, self.context)