import json

from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework import status

# Create your tests here.
class AccountsTest(APITestCase):
	def setUp(self):
		# Contoh default parameter untuk membuat user baru
		self.test_user = User.objects.create_user("testuser", "test@example.com", "testpassword")
		
		# URL membuat user
		self.create_url = reverse("reporter")

	def test_create_user(self):
		"""
		# 1
		Saatnya test membuat user
		"""
		data = {
			"username": "foobar10",
			"email": "foobar10@google.com",
			"password": "somepassword5617#753"
		}
		
		# Simpan data
		response = self.client.post(
			self.create_url, 
			data=json.dumps(data),
			content_type="application/json"
		)
		
		"""
		Jika berhasil membuat akun
		User harus menjadi 2
		"""
		user = User.objects.all()
		self.assertEqual(user.count(), 2)
		
		# Response status kode
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		
		# Jika berhasil dibuat, kita ingin melihat datanya
		self.assertEqual(response.data["username"], data["username"])
		self.assertEqual(response.data["email"], data["email"])
		self.assertFalse("password" in response.data)

	def test_create_user_with_sort_password(self):
		"""
		# 2
		Test password pendek
		"""
		data = {
			"username": "foobar",
			"email": "foobar@google.com",
			"password": "123"
		}
		
		# Simpan data
		response = self.client.post(self.create_url, data, format="json")
		
		# Response status kode
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		
		# Cek apakah ada 1 user
		self.assertEqual(User.objects.count(), 1)
		
		# Jika berhasil dibuat, kita ingin melihat datanya
		self.assertEqual(len(response.data["password"]), 1)

	def test_create_user_user_with_no_password(self):
		"""
		# 3
		Test tanpa password
		"""
		data = {
			"username": "foobar",
			"email": "foobar@google.com",
			"password": ""
		}
		
		# Simpan data
		response = self.client.post(self.create_url, data, format="json")
		
		# Response status kode
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		
		# Cek apakah ada 1 user
		self.assertEqual(User.objects.count(), 1)
		
		# Jika berhasil dibuat, kita ingin melihat datanya
		self.assertEqual(len(response.data["password"]), 1)

	def test_create_user_with_too_long_username(self):
		"""
		# 4
		Test username sangat panjang
		"""
		data = {
			"username": "foobar"*30,
			"email": "foobar@google.com",
			"password": "123456"
		}
		
		# Simpan data
		response = self.client.post(self.create_url, data, format="json")
		
		# Response status kode
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		
		# Cek apakah ada 1 user
		self.assertEqual(User.objects.count(), 1)
		
		# Jika berhasil dibuat, kita ingin melihat datanya
		self.assertEqual(len(response.data["username"]), 1)
		
	def test_create_user_with_no_username(self):
		"""
		# 5
		Test tanpa username
		"""
		data = {
			"username": "",
			"email": "foobar@google.com",
			"password": "123456"
		}
		
		# Simpan data
		response = self.client.post(self.create_url, data, format="json")
		
		# Response status kode
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		
		# Cek apakah ada 1 user
		self.assertEqual(User.objects.count(), 1)
		
		# Jika berhasil dibuat, kita ingin melihat datanya
		self.assertEqual(len(response.data["username"]), 1)

	def test_create_user_with_preexisting_username(self):
		"""
		# 6
		Test username sudah adata
		"""
		data = {
			"username": "testuser",
			"email": "user@example.com",
			"password": "123456"
		}
		
		# Simpan data
		response = self.client.post(self.create_url, data, format="json")
		
		# Response status kode
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		
		# Cek apakah ada 1 user
		self.assertEqual(User.objects.count(), 1)
		
		# Jika berhasil dibuat, kita ingin melihat datanya
		self.assertEqual(len(response.data["username"]), 1)