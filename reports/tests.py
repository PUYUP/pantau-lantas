import json

from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework import status

# Import models
from .models import Vehicle, Violation, PoliceNumber, Reported

# Create your tests here.
class PoliceNumberTest(APITestCase):
	"""
	Testing nomor polisi
	"""
	def setUp(self):
		"""
		Setup
		"""
		# Data
		reporter = User.objects.create_user("testuser", "test@example.com", "ind0nesi@")
		vehicle = Vehicle.objects.create(variety="Motor")
		police_number = "BH8734HI"

		# Paksa login
		self.client.force_login(User.objects.get_or_create(username='testuser')[0])

		# Simpan
		self.test_police_number = PoliceNumber.objects.create(
			reporter=reporter,
			vehicle=vehicle,
			number=police_number
		)

		# Endpoint nomor polisi
		self.create_police_number_url = reverse("police_number")

	def test_police_number_create(self):
		"""
		Buat nomor polisi
		"""
		data = {
			"reporter": 1,
            "number": "BH1230AB",
            "vehicle": 1
        }

		# Simpan data
		response = self.client.post(
			self.create_police_number_url,
			data=json.dumps(data),
			content_type="application/json"
		)

		"""
		Jika berhasil
		Harus menjadi 2
		"""
		police_number = PoliceNumber.objects.all()
		self.assertEqual(police_number.count(), 2)

		# Response status kode
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		# Jika berhasil dibuat, kita ingin melihat datanya
		self.assertEqual(response.data["vehicle"], data["vehicle"])
		self.assertEqual(response.data["number"], data["number"])

	def test_police_number_create_no_number(self):
		"""
		Tanpa nomor polisi maka tidak bisa dibuat
		"""
		data = {
			"reporter": 1,
            "number": "",
            "vehicle": 1
        }

		# Paksa login
		self.client.force_login(User.objects.get_or_create(username='testuser')[0])

		# Simpan data
		response = self.client.post(
			self.create_police_number_url,
			data=json.dumps(data),
			content_type="application/json"
		)

		# Response status kode
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_police_number_create_no_reporter(self):
		"""
		Tanpa reporter maka tidak bisa dibuat
		"""
		data = {
			"reporter": "",
            "number": "BH1230AB",
            "vehicle": 1
        }

		# Paksa login
		self.client.force_login(User.objects.get_or_create(username='testuser')[0])

		# Simpan data
		response = self.client.post(
			self.create_police_number_url,
			data=json.dumps(data),
			content_type="application/json"
		)

		# Response status kode
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_police_number_create_no_vehicle(self):
		"""
		Tanpa jenis kendaraan maka tidak bisa dibuat
		"""
		data = {
			"reporter": 1,
            "number": "BH1230AB",
            "vehicle": ""
        }

		# Paksa login
		self.client.force_login(User.objects.get_or_create(username='testuser')[0])

		# Simpan data
		response = self.client.post(
			self.create_police_number_url,
			data=json.dumps(data),
			content_type="application/json"
		)

		# Response status kode
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ReportedTest(APITestCase):
	"""
	Testing pelaporan
	"""
	def setUp(self):
		"""
		Setup
		"""
		# Data
		reporter = User.objects.create_user("testuser", "test@example.com", "ind0nesi@")
		vehicle = Vehicle.objects.create(variety="Motor")
		violation = Violation.objects.create(variety="Ugalan", description="Berkendara sembarangan")
		police_number = "BH8734HI"
		explanation = "Menyalip sesuka hati"

		# Paksa login
		self.client.force_login(User.objects.get_or_create(username='testuser')[0])

		# Buat nomor polisi
		police_number_obj = PoliceNumber.objects.create(
			reporter=reporter,
			vehicle=vehicle,
			number=police_number
		)

		# Buat laporan
		self.test_reported = Reported.objects.create(
			reporter=reporter,
			violation=violation,
			police_number=police_number_obj,
			explanation=explanation
		)

		# Endpoint laporan
		self.create_report_url = reverse("report")

	def test_reported_create(self):
		"""
		Buat laporan
		"""
		vehicle = Vehicle.objects.first()
		violation = Violation.objects.first()
		
		# Data
		data = {
            "police_number": {
                "number": "BH8734HI",
                "vehicle": vehicle.pk
            },
            "violation": violation.pk
        }

		# Paksa login
		self.client.force_login(User.objects.get_or_create(username='testuser')[0])

		# Simpan data
		response = self.client.post(
			self.create_report_url,
			data=json.dumps(data),
			content_type="application/json"
		)
		
		"""
		Jika berhasil membuat laporan
		Laporan harus menjadi 2
		"""
		reported = Reported.objects.all()
		self.assertEqual(reported.count(), 2)

		# Response status kode
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		# Pastikan hasil ada
		self.assertEqual(response.data["police_number"]["number"], data["police_number"]["number"])
