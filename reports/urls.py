from django.contrib import admin
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import (
	VehicleView,
	ViolationView,
	ReportedView,
	ReportedDetailView,
	PoliceNumberView,
	PoliceNumberDetailView
)

urlpatterns = [
	path('number/', PoliceNumberView.as_view(), name="police_number"),
	path('number/<int:pk>/', PoliceNumberDetailView.as_view(), name="police_number_detail"),
	path('report/', ReportedView.as_view(), name="report"),
	path('report/<int:pk>/', ReportedDetailView.as_view(), name="report_detail"),
	path('vehicle/', VehicleView.as_view(), name="vehicle"),
	path('violation/', ViolationView.as_view(), name="violation"),
]
