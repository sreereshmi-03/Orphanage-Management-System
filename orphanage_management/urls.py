# orphanage_management/urls.py

from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from dashboard.views import custom_dashboard  # Import your custom dashboard view

urlpatterns = [
    # Redirect the root URL to the login page.
    path('', RedirectView.as_view(url='/login/', permanent=False), name='home'),

    # Django Admin (default)
    path('admin/', admin.site.urls),

    # Login URL using Django's built-in LoginView with our custom template.
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html',
        redirect_authenticated_user=True
    ), name='login'),

    # Custom Dashboard URL for admin users.
    path('custom-dashboard/', custom_dashboard, name='custom_dashboard'),
]
