from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from ..models import Animal, MedicalRecord, AnimalPhoto
from .serializers import AnimalSerializer, MedicalRecordSerializer, AnimalPhotoSerializer

class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Simplified permission: Staff users have full access, others read-only
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Staff/superusers can do anything
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Regular authenticated users have read-only access
        return request.method in permissions.SAFE_METHODS

class AnimalViewSet(viewsets.ModelViewSet):
    serializer_class = AnimalSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['species', 'gender', 'behavior', 'adoption_status', 'public_visibility', 'shelter']
    search_fields = ['name', 'chip_id', 'capture_location', 'shelter']
    ordering_fields = ['created_at', 'name', 'entry_date']
    
    def get_queryset(self):
        return Animal.objects.all().prefetch_related('medical_records', 'photos')
    
    @action(detail=True, methods=['get'])
    def medical_records(self, request, pk=None):
        animal = self.get_object()
        records = animal.medical_records.all()
        serializer = MedicalRecordSerializer(records, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def photos(self, request, pk=None):
        animal = self.get_object()
        photos = animal.photos.all()
        serializer = AnimalPhotoSerializer(photos, many=True)
        return Response(serializer.data)

class MedicalRecordViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalRecordSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['animal', 'record_type', 'date_recorded']
    search_fields = ['description', 'animal__name', 'animal__chip_id']
    
    def get_queryset(self):
        return MedicalRecord.objects.all().select_related('animal')

class AnimalPhotoViewSet(viewsets.ModelViewSet):
    serializer_class = AnimalPhotoSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['animal', 'is_primary']
    
    def get_queryset(self):
        return AnimalPhoto.objects.all().select_related('animal')