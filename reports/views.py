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
from reports.models import PoliceNumber, Reported, Vehicle, Violation
from users.models import UserPoliceNumber

# Restful
from reports.serializer import (
	VehicleSerializer,
	ViolationSerializer,
	PoliceNumberSerializer,
	ReportedSerializer
)

from users.serializer import UserPoliceNumberSerializer

# Create your views here.
class VehicleView(APIView):
    """
    List jenis kendaraan
    """
    # Settings
    permission_classes = (AllowAny,)

    def get(self, request, format="json"):
        vehicle = Vehicle.objects.all()
        serializer = VehicleSerializer(vehicle, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ViolationView(APIView):
	"""
	List jenis pelanggaran
	"""
	# Settings
	permission_classes = (AllowAny,)

	def get(self, request, format="json"):
		violation = Violation.objects.all()
		serializer = ViolationSerializer(violation, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)


class PoliceNumberView(APIView):
	"""
	Listing nomor polisi
	"""
	# Settings
	permission_classes = (AllowAny,)

	def get(self, request, format=None):
		police_number = PoliceNumber.objects.annotate(
            num_reported=Count("reported"),
            num_reporter=Count("reporter")
        )
		paginator = PageNumberPagination()
		result_page = paginator.paginate_queryset(police_number, request)
		serializer = PoliceNumberSerializer(result_page, many=True)
		response = {
			"links": {
				"previous": paginator.get_previous_link(),
				"next": paginator.get_next_link(),
			},
			"count": paginator.page.paginator.count,
			"results": serializer.data,
		}
		return Response(response, status=status.HTTP_200_OK)

	@transaction.atomic
	def post(self, request, format=None):
		"""
		Jangan biarkan user menggunakan akun orang lain
		Pastikan user saat ini adalah dirinya sendiri
		User harus login
		"""
		context = {
			"request": self.request
		}

		if request.user.is_authenticated:
			serializer = PoliceNumberSerializer(data=request.data, context=context)

			if serializer.is_valid(raise_exception=True):
				serializer.save()
				return Response(serializer.data, status=status.HTTP_201_CREATED)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		return Response({"errors": "Login required!"}, status=status.HTTP_401_UNAUTHORIZED)


class ReportedView(APIView):
	"""
	Listing laporan
	"""
	# Settings
	permission_classes = (AllowAny,)

	def get(self, request, format=None):
		reported = Reported.objects.all()
		paginator = PageNumberPagination()
		result_page = paginator.paginate_queryset(reported, request)
		serializer = ReportedSerializer(result_page, many=True)
		response = {
			"links": {
				"previous": paginator.get_previous_link(),
				"next": paginator.get_next_link(),
			},
			"count": paginator.page.paginator.count,
			"results": serializer.data,
		}
		return Response(response, status=status.HTTP_200_OK)

	@transaction.atomic
	def post(self, request, format=None):
		"""
		Jangan biarkan user menggunakan akun orang lain
		Pastikan user saat ini adalah dirinya sendiri
		"""
		context = {
			"request": self.request
		}

		if request.user.is_authenticated:
			serializer = ReportedSerializer(data=request.data, context=context)

			if serializer.is_valid(raise_exception=True):
				serializer.save()
				return Response(serializer.data, status=status.HTTP_201_CREATED)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		return Response({"errors": "Login required!"}, status=status.HTTP_401_UNAUTHORIZED)


class ReportedDetailView(APIView):
	"""
	Detail laporan
	Hanya lihat dan hapus, tidak boleh diedit
	"""
	# Settings
	permission_classes = (AllowAny,)

	def get_object(self, pk):
		try:
			return Reported.objects.get(pk=pk)
		except Reported.DoesNotExist:
			raise Http404

	def get(self, request, pk, format="json"):
		reported = self.get_object(pk)
		serializer = ReportedSerializer(reported, many=False)
		return Response(serializer.data, status=status.HTTP_200_OK)

	@transaction.atomic
	def delete(self, request, pk, format="json"):
		if request.user.is_authenticated:
			reported = self.get_object(pk)
			reporter_is_self = True if request.user.username == reported.reporter.username else False

			if reporter_is_self:
				reported.delete()
				return Response(status=status.HTTP_204_NO_CONTENT)
			return Response(status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
		return Response({"errors": "Login required!"}, status=status.HTTP_401_UNAUTHORIZED)


class PoliceNumberDetailView(APIView):
	"""
	Detail nomor polisi
	Tidak boleh edit, hapus, hanya lihat
	"""
	# Settings
	permission_classes = (AllowAny,)

	def get_object(self, pk):
		try:
			return PoliceNumber.objects.get(pk=pk)
		except PoliceNumber.DoesNotExist:
			raise Http404

	def get(self, request, pk, format=None):
		"""
		Nomor polisi
		"""
		police_number = self.get_object(pk)
		serializer_police_number = PoliceNumberSerializer(police_number, many=False)

		"""
		Laporan dari nomor polisi
		"""
		reported = Reported.objects.filter(police_number=police_number)
		paginator = PageNumberPagination()
		result_page = paginator.paginate_queryset(reported, request)
		serializer = ReportedSerializer(result_page, many=True)

		"""
		Apakah nomor polisi ini diklaim user?
		"""
		user_police_number_serializer = None
		if request.user.is_authenticated:
			try:
				user_police_number = UserPoliceNumber.objects.get(
					ownership=request.user,
					vehicle=police_number.vehicle,
					police_number=police_number
				)
			except UserPoliceNumber.DoesNotExist:
				user_police_number = None

			if user_police_number and user_police_number.ownership == request.user:
				user_police_number_serializer = UserPoliceNumberSerializer(user_police_number, many=False)
				user_police_number_serializer = user_police_number_serializer.data

		"""
		Gabungkan keduanya
		"""
		response = {
			"links": {
				"previous": paginator.get_previous_link(),
				"next": paginator.get_next_link(),
			},
			"police_number": serializer_police_number.data,
			"count": paginator.page.paginator.count,
			"reports": serializer.data,
			"user_police_number": user_police_number_serializer,
		}
		return Response(response, status=status.HTTP_200_OK)
