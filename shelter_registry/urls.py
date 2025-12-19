from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from animals.api.views import AnimalViewSet, MedicalRecordViewSet, AnimalPhotoViewSet

# API Router
router = DefaultRouter()
router.register(r'animals', AnimalViewSet, basename='animal')
router.register(r'medical-records', MedicalRecordViewSet, basename='medicalrecord')
router.register(r'photos', AnimalPhotoViewSet, basename='animalphoto')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('', include('animals.urls')),  # Animals URLs at root (includes /adopt/, /qr/, etc)
]