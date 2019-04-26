from django.contrib import admin
from django.urls import path

from .views import HomeView

urlpatterns = [
	path('', HomeView.as_view(), name="home"),
]

# Rubah text
admin.site.site_header = 'Administrasi Awasi Jalan'
admin.site.site_title = 'Administrasi Awasi Jalan'
admin.site.index_title = "Selamat Datang di Portal Awasi Jalan"