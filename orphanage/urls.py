from django.urls import path
from . import views
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/user/', views.register_user, name='register_user'),
    path('register/caretaker/', views.register_caretaker, name='register_caretaker'),
    path('register/child/', views.register_child, name='register_child'),
    path('donate/', views.donate, name='donate'),
    path('adoption/request/', views.adoption_request, name='adoption_request'),
    path('adoption-requests/', views.fetch_adoption_requests, name='fetch_adoption_requests'),
    path('caretakers/', views.fetch_caretakers, name='fetch_caretakers'),
    path('children/', views.fetch_children, name='fetch_children'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/caretaker/', views.caretaker_dashboard, name='caretaker_dashboard'),
    path('home/', views.home, name='home'),
    path('adoption-requests/', views.fetch_adoption_requests, name='adoption_requests_list'),
    path('unauthorized/', TemplateView.as_view(template_name='unauthorized.html'), name='unauthorized'),
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),
    path('caretaker_login/', views.caretaker_login, name='caretaker_login'),
    path('add-report/', views.add_report, name='add_report'),
    path('edit-child/<int:child_id>/', views.edit_child, name='edit_child'),
    path('fetch_reports/', views.fetch_reports, name='fetch_reports'),
    path('fetch_admin_children/', views.fetch_admin_children, name='fetch_admin_children'),
    path('delete_caretaker/<int:caretaker_id>/', views.delete_caretaker, name='delete_caretaker'),
    path('delete_child/<int:child_id>/', views.delete_child, name='delete_child'),
    path('adopted-children/', views.adopted_children_list, name='adopted_children_list'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)