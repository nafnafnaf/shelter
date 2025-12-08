from django import forms
from .models import Animal, MedicalRecord, AnimalPhoto

class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        exclude = ['created_by', 'created_at', 'updated_at', 'entry_date']
        widgets = {
            'chip_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '15-digit chip ID',
                'pattern': '[0-9]{15}',
                'maxlength': '15'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '20'
            }),
            'species': forms.Select(attrs={'class': 'form-select'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'age_numeric': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '99',
                'placeholder': 'Age in years'
            }),
            'age_category': forms.Select(attrs={'class': 'form-select'}),
            'injured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'behavior': forms.Select(attrs={'class': 'form-select'}),
            'vaccination_status': forms.Select(attrs={'class': 'form-select'}),
            'sterilization_status': forms.Select(attrs={'class': 'form-select'}),
            'cage_number': forms.Select(
                choices=[(i, i) for i in range(1, 21)],
                attrs={'class': 'form-select'}
            ),
            'capture_location': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '100'
            }),
            'capture_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'finder_contact': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'public_visibility': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'adoption_status': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make age_category not required since we can use age_numeric instead
        self.fields['age_category'].required = False
        self.fields['age_numeric'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        age_numeric = cleaned_data.get('age_numeric')
        age_category = cleaned_data.get('age_category')
        
        if age_numeric and age_category:
            raise forms.ValidationError('Please provide either numeric age or age category, not both.')
        if not age_numeric and not age_category:
            raise forms.ValidationError('Please provide either numeric age or age category.')
        
        return cleaned_data

class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['record_type', 'description', 'date_recorded']
        widgets = {
            'record_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'maxlength': '300'
            }),
            'date_recorded': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

class AnimalPhotoForm(forms.ModelForm):
    class Meta:
        model = AnimalPhoto
        fields = ['image', 'caption', 'is_primary']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '100',
                'placeholder': 'Optional caption'
            }),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }