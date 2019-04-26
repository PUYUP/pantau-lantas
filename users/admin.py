from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext as _
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.exceptions import NON_FIELD_ERRORS
from django.utils.safestring import mark_safe
from django.utils.html import format_html, format_html_join, html_safe
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.db import IntegrityError
from django.db.models import Q
from django import forms

# Imports models
from reports.models import PoliceNumber, Vehicle
from users.models import UserPoliceNumber, UserPoliceNumberClaim, UserClaimFile

class UserPoliceNumberForm(forms.ModelForm):
	def clean(self):
		"""
		Override the default clean method to check whether this data has
		been already inputted.
		"""
		cleaned_data = super().clean()
		police_number = cleaned_data.get('police_number')
		vehicle_obj = cleaned_data.get('vehicle')
		vehicle = police_number.vehicle
		matching_police_number = UserPoliceNumber.objects.filter(
			police_number=police_number,
			vehicle=vehicle_obj if vehicle_obj else vehicle
		)

		if self.instance and self.instance.pk is None:
			matching_police_number = matching_police_number.exclude(pk=self.instance.pk)

			if vehicle_obj != vehicle and vehicle_obj:
				message = _("Vehicle %s and police number %s not match.") % (police_number.vehicle.variety, police_number.number)
				raise ValidationError(message)

			if matching_police_number.exists():
				message = _("Vehicle %s with police number %s already exists.") % (police_number.vehicle.variety, police_number.number)
				raise ValidationError(message)
		else:
			return cleaned_data


# Extending list display
class UserClaimFileInline(admin.StackedInline):
	model = UserClaimFile

class UserPoliceNumberDisplay(admin.ModelAdmin):
	"""
	Nomor polisi milik pengguna
	"""
	form = UserPoliceNumberForm
	list_display = ["police_number", "ownership", "vehicle", "is_active"]
	readonly_fields = ["vehicle"]

	def save_model(self, request, obj, form, change):
		"""
		Set jenis kendaraan otomatis
		Berdasarkan nomor polisi
		"""
		obj.vehicle = obj.police_number.vehicle
		super().save_model(request, obj, form, change)


class UserPoliceNumberClaimDisplay(admin.ModelAdmin):
	"""
	Nomor polisi di klaim pengguna
	"""
	inlines = [UserClaimFileInline]
	list_display = ["police_number", "claimant", "vehicle", "is_accepted"]
	readonly_fields = ["claim_file"]

	def claim_file(self, instance):
		claim_file = UserClaimFile.objects.filter(claim=instance)
		if claim_file.exists():
			return format_html_join(
			    '\n', '<a href="{}" target="_blank"><img src="{}" height="150" width="auto" /></a>',
			    (
					(
						reverse('admin:%s_%s_change' % (
							file_data.file_management._meta.app_label,
							file_data.file_management._meta.model_name),
							args=(file_data.file_management.pk,)
						),
						file_data.file_management.file.url
					) for file_data in claim_file
				)
			)
		return mark_safe("&mdash;")

	claim_file.short_description = "File lampiran"

	def save_model(self, request, obj, form, change):
		"""
		Jika disetujui assign nomor polisi ke pengguna (UserPoliceNumber)
		"""
		claimant = obj.claimant
		vehicle = obj.vehicle
		police_number = obj.police_number
		is_accepted = obj.is_accepted

		if is_accepted == True:
			try:
				police_number_obj = PoliceNumber.objects.get(vehicle=vehicle, number=police_number)
			except PoliceNumber.DoesNotExist:
				police_number_obj = PoliceNumber.objects.create(
					reporter=claimant,
					vehicle=vehicle,
					number=police_number
				)

			user_police_number, user_police_number_created = UserPoliceNumber.objects.get_or_create(
				ownership=claimant,
				police_number=police_number_obj,
				vehicle=vehicle
			)

			# Update status klaim nomor telepon
			if user_police_number:
				police_number_obj.is_claimed = True
				police_number_obj.is_onclaim = True
				police_number_obj.save()

		elif is_accepted == False and obj.pk:
			try:
				police_number_obj = PoliceNumber.objects.get(vehicle=vehicle, number=police_number)
			except PoliceNumber.DoesNotExist:
				police_number_obj = None

			if police_number_obj:
				# Update status klaim nomor telepon
				police_number_obj.is_claimed = False
				police_number_obj.is_onclaim = False
				police_number_obj.save()

				try:
					user_police_number_obj = UserPoliceNumber.objects.get(
						ownership=claimant,
						vehicle=vehicle,
						police_number=police_number_obj
					)
				except UserPoliceNumber.DoesNotExist:
					user_police_number_obj = None

				if user_police_number_obj:
					user_police_number_obj.delete()

		super().save_model(request, obj, form, change)

# Show to admin
admin.site.register(UserPoliceNumber, UserPoliceNumberDisplay)
admin.site.register(UserPoliceNumberClaim, UserPoliceNumberClaimDisplay)
admin.site.register(UserClaimFile)
