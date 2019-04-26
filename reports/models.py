from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.core.validators import MinLengthValidator, RegexValidator

alphanumeric = RegexValidator(
	regex='^(?=.*[0-9])(?=.*[a-zA-Z])([a-zA-Z0-9]+)+$',
	message='Only alphanumeric characters are allowed.'
)

# Create your models here.
class Violation(models.Model):
	"""
	Jenis laporan/pelanggaran
	"""
	variety = models.CharField(max_length=255, null=True)
	description = models.TextField(max_length=500, null=True)

	class Meta:
		db_table = "reports_violation"
		verbose_name = "Pelanggaran"
		verbose_name_plural = "Pelanggaran"

	def __str__(self):
		return self.variety


class Vehicle(models.Model):
	"""
	Jenis kendaraan
	"""
	variety = models.CharField(max_length=255, null=True)

	class Meta:
		db_table = "reports_vehicle"
		verbose_name = "Jenis Kendaraan"
		verbose_name_plural = "Jenis Kendaraan"

	def __str__(self):
		return self.variety


class PoliceNumber(models.Model):
	"""
	Nomor polisi dilaporkan
	"""
	reporter = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name="police_number_reported",
		db_column="reporter"
	)
	vehicle = models.ForeignKey(
		Vehicle,
		on_delete=models.CASCADE,
		related_name="police_number_reported",
		db_column="vehicle"
	)
	number = models.CharField(
		validators=[MinLengthValidator(3), alphanumeric],
		max_length=255,
		null=True
	)
	date_created = models.DateTimeField(auto_now_add=True, null=True)
	date_updated = models.DateTimeField(auto_now=True, null=True)
	is_claimed = models.NullBooleanField()
	is_onclaim = models.NullBooleanField()

	class Meta:
		db_table = "reports_police_number"
		unique_together = ["vehicle", "number"]
		ordering = ["-date_created"]
		verbose_name = "Nomor Polisi"
		verbose_name_plural = "Nomor Polisi"

	def __str__(self):
		return '%s: %s' % (self.number, self.vehicle.variety)


class Reported(models.Model):
	"""
	Data laporan pelanggaran
	"""
	reporter = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name="reported",
		db_column="reporter"
	)
	violation = models.ForeignKey(
		Violation,
		on_delete=models.CASCADE,
		related_name="reported",
		db_column="violation"
	)
	police_number = models.ForeignKey(
		PoliceNumber,
		on_delete=models.CASCADE,
		related_name="reported",
		db_column="police_number"
	)
	explanation = models.TextField(
		max_length=500,
		null=True,
		blank=True
	)
	picture = models.ImageField(
		upload_to="picture/",
		max_length=500,
		null=True,
		blank=True
	)
	location = models.TextField(
		max_length=500,
		null=True,
		blank=True
	)
	location_lat = models.CharField(
		max_length=255,
		null=True,
		blank=True
	)
	location_lon = models.CharField(
		max_length=255,
		null=True,
		blank=True
	)
	date_created = models.DateTimeField(auto_now_add=True, null=True)
	date_updated = models.DateTimeField(auto_now=True, null=True)

	class Meta:
		db_table = "reports_reported"
		ordering = ["-date_created"]
		verbose_name = "Laporan"
		verbose_name_plural = "Laporan"

	def __str__(self):
		return self.police_number.number
