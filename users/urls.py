from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
	UserView,
	UserDetailView,
	UserPoliceNumberView,
	UserPoliceNumberDetailView,
	UserPoliceNumberClaimView,
	UserPoliceNumberClaimDetailView,
	TokenObtainPairViewExtend
)

urlpatterns = [
	path('reporter/', UserView.as_view(), name="reporter"),
	path('reporter/<int:pk>/', UserDetailView.as_view(), name="reporter_detail"),
	path('reporter/number/', UserPoliceNumberView.as_view(), name="reporter_number"),
	path('reporter/number/<int:pk>/', UserPoliceNumberDetailView.as_view(), name="reporter_number"),
	path('reporter/claim/', UserPoliceNumberClaimView.as_view(), name="reporter_claim"),
	path('reporter/claim/<int:pk>/', UserPoliceNumberClaimDetailView.as_view(), name="reporter_claim_detail"),

	path('token/', TokenObtainPairViewExtend.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
