from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import EventViewSet, BookingViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='api_events')
router.register(r'bookings', BookingViewSet, basename='api_bookings')
router.register(r'categories', CategoryViewSet, basename='api_categories')

urlpatterns = [
    path('', include(router.urls)),
]