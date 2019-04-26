from django.urls import path

from mains.views import (
	HomeView,
	FileManagementView,
	FileManagementDetailView,
	FileManagementTypeView
)

urlpatterns = [
	path('', HomeView.as_view(), name="home"),
	path('api/file/', FileManagementView.as_view(), name="file_management"),
	path('api/file/<int:pk>/', FileManagementDetailView.as_view(), name="file_management_detail"),
	path('api/file/type/', FileManagementTypeView.as_view(), name="file_management_type")
]
