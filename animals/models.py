from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
import qrcode
from io import BytesIO
from django.core.files import File
from django.conf import settings
import json

class Animal(models.Model):
    SPECIES_CHOICES = [
        ('dog', 'Σκύλος'),
        ('cat', 'Γάτα'),
        ('other', 'Άλλο'),
    ]
    
    GENDER_CHOICES = [
        ('male', 'Αρσενικό'),
        ('female', 'Θηλυκό'),
    ]
    
    AGE_CATEGORY_CHOICES = [
        ('κουταβι', 'Κουτάβι'),
        ('υπερηλικο', 'Υπερήλικο'),
    ]
    
    BEHAVIOR_CHOICES = [
        ('ΗΡΕΜΟ', 'Ήρεμο'),
        ('ΦΟΒΙΚΟ', 'Φοβικό'),
        ('ΑΓΡΙΟ', 'Άγριο'),
        ('ΕΠΙΚΙΝΔΥΝΟ-ΚΑΡΑΝΤΙΝΑ', 'Επικίνδυνο-Καραντίνα'),
    ]
    
    VACCINATION_CHOICES = [
        ('ΕΜΒΟΛΙΟ_1', 'Εμβόλιο 1'),
        ('ΕΜΒΟΛΙΟ_2', 'Εμβόλιο 2'),
        ('ΕΜΒΟΛΙΟ_3', 'Εμβόλιο 3'),
        ('ΕΜΒΟΛΙΟ_4', 'Εμβόλιο 4'),
        ('ΕΜΒΟΛΙΟ_5', 'Εμβόλιο 5'),
        ('ΕΜΒΟΛΙΟ_6', 'Εμβόλιο 6'),
    ]
    
    STERILIZATION_CHOICES = [
        ('yes', 'Ναι'),
        ('no', 'Όχι'),
        ('scheduled', 'Προγραμματισμένο'),
    ]
    
    ADOPTION_STATUS_CHOICES = [
        ('available', 'Διαθέσιμο'),
        ('pending', 'Εκκρεμεί'),
        ('adopted', 'Υιοθετήθηκε'),
        ('not_for_adoption', 'Μη διαθέσιμο για υιοθεσία'),
    ]

    # Basic Information
    chip_id = models.CharField(
        max_length=15,
        unique=True,
        validators=[RegexValidator(r'^\d{15}$', 'Chip ID must be exactly 15 digits')]
    )
    species = models.CharField(max_length=10, choices=SPECIES_CHOICES)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    
    # Age - either numeric age OR category
    age_numeric = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(99)]
    )
    age_category = models.CharField(
        max_length=15, 
        choices=AGE_CATEGORY_CHOICES,
        null=True, blank=True
    )
    
    name = models.CharField(max_length=20)
    
    # Health and Behavior
    injured = models.BooleanField(default=False, verbose_name='Τραυματισμένο')
    behavior = models.CharField(max_length=25, choices=BEHAVIOR_CHOICES)
    vaccination_status = models.CharField(max_length=15, choices=VACCINATION_CHOICES)
    sterilization_status = models.CharField(max_length=15, choices=STERILIZATION_CHOICES)
    
    # Location and Housing
    cage_number = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    
    # Dates and Location
    entry_date = models.DateTimeField(auto_now_add=True)
    capture_location = models.CharField(max_length=100)
    capture_date = models.DateField()
    
    # Contact and Adoption
    finder_contact = models.TextField(blank=True, verbose_name='Στοιχεία του ευρέτη')
    public_visibility = models.BooleanField(default=False, verbose_name='Δημόσια προβολή')
    adoption_status = models.CharField(max_length=20, choices=ADOPTION_STATUS_CHOICES, default='available')
    
    # QR Code
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True, verbose_name='QR Code')
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.chip_id})"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        # Ensure either numeric age OR category is provided, not both
        if self.age_numeric and self.age_category:
            raise ValidationError('Provide either numeric age or age category, not both.')
        if not self.age_numeric and not self.age_category:
            raise ValidationError('Either numeric age or age category must be provided.')
    
    def get_qr_data(self):
        """Generate structured data for QR code"""
        try:
            from django.contrib.sites.models import Site
            current_site = Site.objects.get_current()
            base_url = f"https://{current_site.domain}"
        except:
            base_url = "http://localhost:8000"
        
        return {
            "chip_id": self.chip_id,
            "name": self.name,
            "api_url": f"{base_url}/api/v1/animals/{self.id}/",
            "public_url": f"{base_url}/adopt/{self.id}/",
            "species": self.get_species_display(),
            "gender": self.get_gender_display(),
            "cage": self.cage_number,
            "entry_date": self.entry_date.isoformat(),
        }
    
    def generate_qr_code(self):
        """Generate QR code containing animal information"""
        try:
            # Create QR data as JSON string
            qr_data = json.dumps(self.get_qr_data(), ensure_ascii=False)
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save to BytesIO
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Save to model
            filename = f'qr_{self.chip_id}.png'
            self.qr_code.save(filename, File(buffer), save=False)
            buffer.close()
            
        except Exception as e:
            # Log error but don't fail the save
            print(f"Error generating QR code for animal {self.chip_id}: {e}")
    
    def save(self, *args, **kwargs):
        # Save first to ensure we have an ID
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Generate QR code if it doesn't exist or if this is a new animal
        if is_new or not self.qr_code:
            self.generate_qr_code()
            if self.qr_code:  # Only update if QR generation succeeded
                super().save(update_fields=['qr_code'])


class MedicalRecord(models.Model):
    RECORD_TYPE_CHOICES = [
        ('pathology', 'Παθήσεις'),
        ('diagnosis', 'Διαγνώσεις'),
    ]
    
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='medical_records')
    record_type = models.CharField(max_length=15, choices=RECORD_TYPE_CHOICES)
    description = models.TextField(max_length=300)
    date_recorded = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_recorded']
    
    def __str__(self):
        return f"{self.animal.name} - {self.get_record_type_display()}"


class AnimalPhoto(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='animal_photos/')
    is_primary = models.BooleanField(default=False)
    caption = models.CharField(max_length=100, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-is_primary', '-uploaded_at']
    
    def __str__(self):
        return f"Photo of {self.animal.name}"