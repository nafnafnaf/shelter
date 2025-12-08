from rest_framework import serializers
from ..models import Animal, MedicalRecord, AnimalPhoto

class AnimalPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimalPhoto
        fields = '__all__'

class MedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = '__all__'

class AnimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = '__all__'
