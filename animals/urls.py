from django.urls import path
from . import views
from .qr_scanner import scan_qr_code, qr_scanner_page, public_qr_lookup

app_name = 'animals'

urlpatterns = [
    # Web interface URLs
    path('', views.AnimalListView.as_view(), name='animal_list'),
    path('animal/add/', views.AnimalCreateView.as_view(), name='animal_create'),
    path('animal/<int:pk>/', views.AnimalDetailView.as_view(), name='animal_detail'),
    path('animal/<int:pk>/edit/', views.AnimalUpdateView.as_view(), name='animal_update'),
    path('animal/<int:pk>/delete/', views.AnimalDeleteView.as_view(), name='animal_delete'),
    
    # QR Code functionality
    path('qr/scanner/', qr_scanner_page, name='qr_scanner'),
    path('api/v1/qr/scan/', scan_qr_code, name='qr_scan'),
    path('api/v1/qr/lookup/', public_qr_lookup, name='qr_lookup'),
    
    # Public adoption page
    path('adopt/', views.PublicAdoptionView.as_view(), name='public_adoption'),
    path('adopt/<int:pk>/', views.PublicAnimalDetailView.as_view(), name='public_animal_detail'),
    
    # Medical records
    path('animal/<int:animal_id>/medical/add/', views.MedicalRecordCreateView.as_view(), name='medical_record_create'),
    
    # Photo management
    path('animal/<int:animal_id>/photos/', views.AnimalPhotoListView.as_view(), name='animal_photos'),
]