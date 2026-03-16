# accounts/api_urls.py  (REST API)
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .api_views import CustomTokenObtainPairView, RegisterAPIView, MeAPIView

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterAPIView.as_view(), name='api_register'),
    path('me/', MeAPIView.as_view(), name='api_me'),
]