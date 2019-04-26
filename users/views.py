from django.shortcuts import render
from django.views import View
from django.db import transaction
from django.contrib.auth.models import User
from django.http import Http404

from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

# JWT --> https://github.com/davesque/django-rest-framework-simplejwt
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Serializers
from users.serializer import (
	UserSerializer,
	UserPoliceNumberSerializer,
	UserPoliceNumberClaimSerializer
)

# Imports models
from users.models import UserPoliceNumber, UserPoliceNumberClaim
from reports.models import PoliceNumber

# Create your views here.
class UserView(APIView):
	"""
	Buat user baru
	"""
	# Settings
	permission_classes = (AllowAny,)

	def get_del(self, request, format="json"):
		reporter = User.objects.all()
		paginator = PageNumberPagination()
		result_page = paginator.paginate_queryset(reporter, request)
		serializer = UserSerializer(result_page, many=True)
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
	def post(self, request, format="json"):
		serializer = UserSerializer(data=request.data)

		if serializer.is_valid():
			"""
			Email harus unik
			Satu akun satu email
			"""
			email = request.data["email"]
			username = request.data["username"]
			if email and User.objects.filter(email=email).exclude(username=username).exists():
				return Response(
					{
						"email": ["Email has been used."]
					},
					status=status.HTTP_400_BAD_REQUEST
				)

			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
	"""
	Detail pelapor
	"""
	# Settings
	permission_classes = (AllowAny,)

	def get_object(self, pk):
		try:
			return User.objects.get(pk=pk)
		except User.DoesNotExist:
			raise Http404

	def get(self, request, pk, format="json"):
		reported = self.get_object(pk)
		serializer = UserSerializer(reported, many=False)
		return Response(serializer.data, status=status.HTTP_200_OK)


class TokenObtainPairSerializerExtend(TokenObtainPairSerializer):
	"""
	Modifikasi response token
	"""
	def validate(self, attrs):
		data = super().validate(attrs)
		refresh = self.get_token(self.user)

		data['refresh'] = str(refresh)
		data['access'] = str(refresh.access_token)
		data['user_id'] = self.user.pk
		data['username'] = self.user.username
		return data

class TokenObtainPairViewExtend(TokenObtainPairView):
	serializer_class = TokenObtainPairSerializerExtend


class UserPoliceNumberView(APIView):
	"""
	Daftar nomor polisi milik saya
	"""
	# Settings
	permission_classes = (AllowAny,)

	def get(self, request, format="json"):
		if self.request.user.is_authenticated:
			number = UserPoliceNumber.objects.filter(ownership=self.request.user)
			paginator = PageNumberPagination()
			result_page = paginator.paginate_queryset(number, request)
			serializer = UserPoliceNumberSerializer(result_page, many=True)
			response = {
				"links": {
					"previous": paginator.get_previous_link(),
					"next": paginator.get_next_link(),
				},
				"count": paginator.page.paginator.count,
				"results": serializer.data,
			}
			return Response(response, status=status.HTTP_200_OK)
		return Response({"errors": "Login required!"}, status=status.HTTP_401_UNAUTHORIZED)


class UserPoliceNumberDetailView(APIView):
	"""
	Detail nomor polisi Pengguna
	"""
	# Settings
	permission_classes = (AllowAny,)

	def get_object(self, pk, user):
		try:
			return UserPoliceNumber.objects.get(pk=pk, ownership=user.pk)
		except UserPoliceNumber.DoesNotExist:
			raise Http404

	def get(self, request, pk, format="json"):
		context = {
			"request": self.request
		}

		if request.user.is_authenticated:
			user = self.request.user
			user_police_number = self.get_object(pk, user)
			serializer = UserPoliceNumberSerializer(user_police_number, many=False, context=context)
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response({"errors": "Login required!"}, status=status.HTTP_401_UNAUTHORIZED)

	@transaction.atomic
	def delete(self, request, pk, format="json"):
		if request.user.is_authenticated:
			user = self.request.user
			user_police_number = self.get_object(pk, user)
			police_number = user_police_number.police_number
			ownership_is_self = True if request.user.username == user_police_number.ownership.username else False

			# Hapus claim juga
			try:
				user_claim = UserPoliceNumberClaim.objects.get(
					claimant=request.user,
					vehicle=police_number.vehicle,
					police_number=police_number.number
				)
			except UserPoliceNumberClaim.DoesNotExist:
				user_claim = None

			if ownership_is_self:
				# Reset claim status nomor polisi
				police_number.is_onclaim = False
				police_number.is_claimed = False
				police_number.save()

				# Jika nomor polisi user dihapus
				# Hapus juga di daftar claim
				if user_claim:
					user_claim.delete()

				user_police_number.delete()
				return Response(status=status.HTTP_204_NO_CONTENT)
			return Response(status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
		return Response({"errors": "Login required!"}, status=status.HTTP_401_UNAUTHORIZED)


class UserPoliceNumberClaimView(APIView):
	"""
	Klaim nomor polisi
	"""
	# Settings
	permission_classes = (AllowAny,)

	def get(self, request, format="json"):
		context = {
			"request": self.request
		}

		if self.request.user.is_authenticated:
			claim = UserPoliceNumberClaim.objects.filter(claimant=self.request.user)
			paginator = PageNumberPagination()
			result_page = paginator.paginate_queryset(claim, request)
			serializer = UserPoliceNumberClaimSerializer(result_page, many=True, context=context)
			response = {
				"links": {
					"previous": paginator.get_previous_link(),
					"next": paginator.get_next_link(),
				},
				"count": paginator.page.paginator.count,
				"results": serializer.data,
			}
			return Response(response, status=status.HTTP_200_OK)
		return Response({"errors": "Login required!"}, status=status.HTTP_401_UNAUTHORIZED)

	@transaction.atomic
	def post(self, request, format="json"):
		"""
		Simpan klaim
		"""
		context = {
			"request": self.request
		}

		if request.user.is_authenticated:
			serializer = UserPoliceNumberClaimSerializer(data=request.data, context=context)

			if serializer.is_valid(raise_exception=True):
				serializer.save()
				return Response(serializer.data, status=status.HTTP_201_CREATED)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		return Response({"errors": "Login required!"}, status=status.HTTP_401_UNAUTHORIZED)


class UserPoliceNumberClaimDetailView(APIView):
	"""
	Detail claim
	"""
	# Settings
	permission_classes = (AllowAny,)

	def get_object(self, pk, user):
		try:
			return UserPoliceNumberClaim.objects.get(pk=pk, claimant=user.pk)
		except UserPoliceNumberClaim.DoesNotExist:
			raise Http404

	def get(self, request, pk, format="json"):
		context = {
			"request": self.request
		}

		if request.user.is_authenticated:
			user = self.request.user
			claim = self.get_object(pk, user)
			serializer = UserPoliceNumberClaimSerializer(claim, many=False, context=context)
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response({"errors": "Login required!"}, status=status.HTTP_401_UNAUTHORIZED)

	@transaction.atomic
	def put(self, request, pk, format="json"):
		context = {
			"request": self.request
		}

		if request.user.is_authenticated:
			user = self.request.user
			claim = self.get_object(pk, user)
			serializer = UserPoliceNumberClaimSerializer(claim, data=request.data, context=context)
			if serializer.is_valid(raise_exception=True):
				serializer.save()
				return Response(serializer.data, status=status.HTTP_201_CREATED)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		return Response({"errors": "Login required!"}, status=status.HTTP_401_UNAUTHORIZED)

	@transaction.atomic
	def delete(self, request, pk, format="json"):
		if request.user.is_authenticated:
			user = self.request.user
			claim = self.get_object(pk, user)
			claimant_is_self = True if request.user.username == claim.claimant.username else False

			try:
				police_number_obj = PoliceNumber.objects.get(number=claim.police_number, vehicle=claim.vehicle)
			except PoliceNumber.DoesNotExist:
				police_number_obj = None

			if claimant_is_self:
				# Reset status claim nomor polisi
				if police_number_obj and (police_number_obj.is_claimed is None or police_number_obj.is_claimed == False):
					police_number_obj.is_onclaim = False
					police_number_obj.save()

				claim.delete()
				return Response(status=status.HTTP_204_NO_CONTENT)
			return Response(status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
		return Response({"errors": "Login required!"}, status=status.HTTP_401_UNAUTHORIZED)
