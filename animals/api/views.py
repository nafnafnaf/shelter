from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from ..models import Animal, MedicalRecord, AnimalPhoto
from .serializers import AnimalSerializer, MedicalRecordSerializer, AnimalPhotoSerializer
from shelter.models import ShelterUser

class IsAdminOrEmployeeReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        try:
            shelter_user = ShelterUser.objects.get(user=request.user)
            if shelter_user.role == 'admin':
                return True
            elif shelter_user.role == 'employee':
                return request.method in ['GET', 'POST', 'PUT', 'PATCH', 'HEAD', 'OPTIONS']
            return False
        except ShelterUser.DoesNotExist:
            return False

class AnimalViewSet(viewsets.ModelViewSet):
    serializer_class = AnimalSerializer
    permission_classes = [IsAdminOrEmployeeReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['species', 'gender', 'behavior', 'adoption_status', 'public_visibility']
    search_fields = ['name', 'chip_id', 'capture_location']
    ordering_fields = ['created_at', 'name', 'entry_date']
    ordering = ['-created_at']

    def get_queryset(self):
        return Animal.objects.all().prefetch_related('medical_records', 'photos')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class MedicalRecordViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalRecordSerializer
    permission_classes = [IsAdminOrEmployeeReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['record_type', 'animal']
    ordering = ['-date_recorded']

    def get_queryset(self):
        return MedicalRecord.objects.all().select_related('animal', 'created_by')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class AnimalPhotoViewSet(viewsets.ModelViewSet):
    serializer_class = AnimalPhotoSerializer
    permission_classes = [IsAdminOrEmployeeReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['animal', 'is_primary']

    def get_queryset(self):
        return AnimalPhoto.objects.all().select_related('animal', 'uploaded_by')

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
