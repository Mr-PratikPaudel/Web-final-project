from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Frontend views
    path('', include('events.urls')),
    path('accounts/', include('accounts.urls')),

    # REST API
    path('api/', include('events.api_urls')),
    path('api/auth/', include('accounts.api_urls')),
]