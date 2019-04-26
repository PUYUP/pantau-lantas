import os

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Min, Sum

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

# Imports models
from reports.models import PoliceNumber
from users.models import UserPoliceNumber, UserPoliceNumberClaim, UserClaimFile

# Serializers
from reports.serializer import PoliceNumberSerializer
from mains.serializer import FileManagementSerializer

# Create serializers
class UserSerializer(serializers.ModelSerializer):
	"""
	Buat akun baru
	"""
	class Meta:
		model = User
		fields = ["username", "email", "password"]
		extra_kwargs = {
			'password': {
				'write_only': True,
				'min_length': 8
			},
			'email': {'write_only': True}
		}

	def create(self, validated_data):
		user = User.objects.create_user(**validated_data)
		return user


class UserPoliceNumberSerializer(serializers.ModelSerializer):
	"""
	Daftar nomor polisi milik saya
	"""
	police_number = PoliceNumberSerializer(many=False)
	reported_count = serializers.SerializerMethodField(read_only=True)

	# Hitung jumlah laporan dari nomor polisi
	def get_reported_count(self, user_police_number):
		if user_police_number.police_number is not None:
			try:
				police_number_reported = PoliceNumber.objects.filter(
					number=user_police_number.police_number.number,
					vehicle=user_police_number.police_number.vehicle.pk
				)
			except PoliceNumber.DoesNotExist:
				police_number_reported = None

			if police_number_reported:
				return police_number_reported.annotate(num_reported=Count("reported"))[0].num_reported
			else:
				return 0
		return 0

	class Meta:
		model = UserPoliceNumber
		fields = "__all__"


class UserClaimFileSerializer(serializers.ModelSerializer):
	"""
	File claim, ex: KTP, dll
	"""
	file_name = serializers.SerializerMethodField(read_only=True)
	file_url = serializers.SerializerMethodField(read_only=True)
	file_label = serializers.CharField(source="file_type.type", read_only=True)

	class Meta:
		model = UserClaimFile
		fields = ["file_name", "file_url", "date_created", "file_management", "file_type", "file_label"]
		extra_kwargs = {
			# 'file_management': {'write_only': True},
			# 'file_type': {'write_only': True}
		}

	def get_file_name(self, obj):
		if (obj.file_management is not None):
			return os.path.basename(obj.file_management.file.name)
		return None

	def get_file_url(self, obj):
		if (obj.file_management is not None):
			request = self.context["request"]
			file_url = obj.file_management.file.url
			return request.build_absolute_uri(file_url)
		return None


class UserPoliceNumberClaimSerializer(serializers.ModelSerializer):
	"""
	Klaim nomor polisi
	"""
	claimant = serializers.HiddenField(default=serializers.CurrentUserDefault())
	users_claim_file = UserClaimFileSerializer(many=True) # Gunakan related_name

	class Meta:
		model = UserPoliceNumberClaim
		fields = "__all__"
		read_only_fields = [
			"id", "date_created", "date_updated",
			"is_accepted"
		]

	def create(self, validated_data):
		users_claim_file = validated_data.pop("users_claim_file")
		claim, created = UserPoliceNumberClaim.objects.get_or_create(**validated_data)

		police_number = validated_data.get("police_number")
		vehicle = validated_data.get("vehicle")

		# Update nomor polisi dalam proses klaim
		try:
			police_number_obj = PoliceNumber.objects.get(vehicle=vehicle, number=police_number)
		except PoliceNumber.DoesNotExist:
			police_number_obj = None

		if police_number_obj:
			# Update status klaim nomor telepon
			police_number_obj.is_onclaim = True
			police_number_obj.save()

		for file_data in users_claim_file:
			UserClaimFile.objects.create(claim=claim, **file_data)
		return claim

	def update(self, instance, validated_data):
		users_claim_file = validated_data.pop("users_claim_file")
		files = (instance.users_claim_file).all()
		files = list(files)
		files_id = []
		files_init_id = []

		instance.claimant = validated_data.get('claimant', instance.claimant)
		instance.vehicle = validated_data.get('vehicle', instance.vehicle)
		instance.police_number = validated_data.get('police_number', instance.police_number)
		instance.save()

		# Ekstrak file management dari yang tersimpan
		for file in files:
			files_id.append(file.file_management)

		# Ekstrak file management dari yang user berikan
		for file in users_claim_file:
			files_init_id.append(file["file_management"])

		# Bandingkan keduanya lalu ambil yang berbeda
		remove_files = (list(set(files_id) - set(files_init_id)))

		# Hapus file claim
		if remove_files:
			for file in remove_files:
				file.delete()

		for file_data in users_claim_file:
			if files:
				file = files.pop(0)
				file.file_management = file_data.get('file_management', file.file_management)
				file.file_type = file_data.get('file_type', file.file_type)
				file.save()
			else:
				UserClaimFile.objects.get_or_create(claim=instance, **file_data)
		return instance
