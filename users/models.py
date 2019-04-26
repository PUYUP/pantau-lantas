from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, RegexValidator

# Imports models
from reports.models import Vehicle, PoliceNumber
from mains.models import FileManagement, FileManagementType

alphanumeric = RegexValidator(
	regex='^(?=.*[0-9])(?=.*[a-zA-Z])([a-zA-Z0-9]+)+$',
	message='Only alphanumeric characters are allowed.'
)

# Create your models here.
class UserPoliceNumber(models.Model):
	"""
	Data nomor polisi yang dimiliki pengguna
	"""
	ownership = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name="police_number_user",
		db_column="ownership"
	)
	vehicle = models.ForeignKey(
		Vehicle,
		on_delete=models.CASCADE,
		related_name="police_number_user",
		db_column="vehicle"
	)
	police_number = models.ForeignKey(
		PoliceNumber,
		on_delete=models.CASCADE,
		related_name="police_number_user",
		db_column="police_number",
		null=True
	)
	date_created = models.DateTimeField(auto_now_add=True, null=True)
	date_updated = models.DateTimeField(auto_now=True, null=True)
	is_active = models.NullBooleanField()

	class Meta:
		db_table = "users_police_number"
		unique_together = ["ownership", "police_number", "vehicle"]
		ordering = ["-date_created"]
		verbose_name = "Nomor Polisi Pengguna"
		verbose_name_plural = "Nomor Polisi Pengguna"

	def __str__(self):
		return self.police_number.number


class UserPoliceNumberClaim(models.Model):
	"""
	Klaim nomor polisi
	"""
	claimant = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name="police_number_claim",
		db_column="claimant"
	)
	vehicle = models.ForeignKey(
		Vehicle,
		on_delete=models.CASCADE,
		related_name="police_number_claim",
		db_column="vehicle"
	)
	police_number = models.CharField(
		validators=[MinLengthValidator(3), alphanumeric],
		max_length=255,
		null=True
	)
	date_created = models.DateTimeField(auto_now_add=True, null=True)
	date_updated = models.DateTimeField(auto_now=True, null=True)
	is_accepted = models.NullBooleanField()

	class Meta:
		db_table = "users_claim"
		unique_together = ["claimant", "police_number", "vehicle"]
		ordering = ["-date_created"]
		verbose_name = "Klaim Nomor Polisi"
		verbose_name_plural = "Klaim Nomor Polisi"

	def __str__(self):
		return self.police_number


class UserClaimFile(models.Model):
	claim = models.ForeignKey(
		UserPoliceNumberClaim,
		on_delete=models.CASCADE,
		related_name="users_claim_file"
	)
	file_management = models.ForeignKey(
		FileManagement,
		on_delete=models.CASCADE,
		related_name="users_claim_file"
	)
	file_type = models.ForeignKey(
		FileManagementType,
		on_delete=models.CASCADE,
		related_name="users_claim_file",
		blank=False, 
		null=True,
	)
	date_created = models.DateTimeField(auto_now_add=True, null=True)

	class Meta:
		db_table = "users_claim_file"
		ordering = ["-date_created"]

	def __str__(self):
		return self.file_management.file.name
