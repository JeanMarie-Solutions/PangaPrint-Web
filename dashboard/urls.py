from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('upload/', views.upload_pdf, name='upload_pdf'),
    path('profiles/', views.printer_profiles, name='printer_profiles'),
    path('profiles/<int:pk>/edit/', views.edit_printer_profile, name='edit_printer_profile'),
    path('profiles/<int:pk>/delete/', views.delete_printer_profile, name='delete_printer_profile'),
    path('history/', views.processing_history, name='processing_history'),
    path('history/<int:pk>/download/', views.download_processed, name='download_processed'),
    path('history/<int:pk>/print/', views.print_processed, name='print_processed'),
    path('history/<int:pk>/delete/', views.delete_processing_history, name='delete_processing_history'),
    path('about/', views.about, name='about'),
    path('api/profiles/', views.api_profiles, name='api_profiles'),

    # API endpoints
    path('api/status/', views.api_status, name='api_status'),
    path('api/process/', views.api_process_job, name='api_process_job'),
]