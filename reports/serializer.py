from django.contrib.auth.models import User
from django.db.models import Avg, Count, Min, Sum
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from rest_framework import routers, serializers, viewsets
from rest_framework.response import Response
from rest_framework.validators import UniqueTogetherValidator

# Import models
from .models import Violation, Vehicle, PoliceNumber, Reported

# Create serializers
class ViolationSerializer(serializers.ModelSerializer):
	"""
	Serialize Violation
	"""
	id = serializers.IntegerField(read_only=True)

	class Meta:
		model = Violation
		fields = "__all__"


class VehicleSerializer(serializers.ModelSerializer):
	"""
	Serialize Vehicle
	"""
	id = serializers.IntegerField(read_only=True)

	class Meta:
		model = Vehicle
		fields = "__all__"


class PoliceNumberSerializer(serializers.ModelSerializer):
	"""
	Serialize PoliceNumber
	"""
	reported_count = serializers.IntegerField(read_only=True, source="num_reported")
	reporter_count = serializers.IntegerField(read_only=True, source="num_reporter")
	reporter = serializers.HiddenField(default=serializers.CurrentUserDefault())

	class Meta:
		model = PoliceNumber
		fields = "__all__"
		read_only_fields = [
			"id", "reported_count", "reporter_count",
			"date_created", "date_updated", "is_claimed"
		]
		extra_kwargs = {
			'reporter': {'write_only': True}
		}
		validators = [
			UniqueTogetherValidator(
				queryset=PoliceNumber.objects.all(),
				fields=["vehicle", "number"]
			)
		]

	def create(self, validated_data):
		police_number, created = PoliceNumber.objects.get_or_create(**validated_data)
		return police_number


class ReportedSerializer(serializers.ModelSerializer):
	"""
	Serialize Reported
	"""
	police_number = PoliceNumberSerializer(read_only=False, validators=[])
	reported_count = serializers.SerializerMethodField(read_only=True)
	reporter = serializers.HiddenField(default=serializers.CurrentUserDefault())
	violation_variety = serializers.CharField(read_only=True, source="violation.variety")

	def get_reported_count(self, obj):
		if hasattr(obj, "police_number") and obj.police_number is not None:
			try:
				police_number_reported = PoliceNumber.objects.filter(
					number=obj.police_number.number,
					vehicle=obj.police_number.vehicle.pk
				)
			except PoliceNumber.DoesNotExist:
				police_number_reported = None

			if police_number_reported:
				return police_number_reported.annotate(num_reported=Count("reported"))[0].num_reported
			else:
				return 0
		return 0

	class Meta:
		model = Reported
		fields = "__all__"
		read_only_fields = [
			"id", "reported_count", "date_created",
			"date_updated"
		]
		extra_kwargs = {
			"reporter": {"write_only": True}
		}

	def create(self, validated_data):
		police_number = validated_data.pop("police_number")
		
		try:
			police_number_create, created = PoliceNumber.objects.get_or_create(
				number=police_number.get("number"), vehicle=police_number.get("vehicle"),
				defaults=police_number
			)
		except IntegrityError:
			police_number_create = None
		
		if police_number_create:
			return Reported.objects.create(police_number=police_number_create, **validated_data)
		raise serializers.ValidationError({"error": "Data invalid."});