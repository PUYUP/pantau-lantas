from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Kategori(models.Model):
    nama_kategori = models.CharField(max_length=100)

class Buku(models.Model):
    penulis = models.ForeignKey(User, on_delete=models.CASCADE, related_name="buku")
    kategori = models.ForeignKey(Kategori, on_delete=models.CASCADE, related_name="buku")
    judul = models.CharField(max_length=100)
    penerbit = models.CharField(max_length=100)

    def __str__(self):
        return '%: %', (self.penulis.username, self.judul)
