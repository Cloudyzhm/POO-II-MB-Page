from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', include('users.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('tickets/', include('tickets.urls')),
    path('', include('landing.urls')),
]
