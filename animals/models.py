from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
import qrcode
from io import BytesIO
from django.core.files import File
from django.conf import settings
import json
import os

def get_default_shelter_name():
    """Get default shelter name from environment"""
    return os.environ.get('ORGANIZATION_NAME', 'Καταφύγιο Εθελοντών Δήμου Καβάλας - Πολύστυλο')

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
        ('ΕΜΒΟΛΙΟ_1', 'DHPP'),
        ('ΕΜΒΟΛΙΟ_2', 'DHPPI'),
        ('ΕΜΒΟΛΙΟ_3', 'Carre (Distemper)'),
        ('ΕΜΒΟΛΙΟ_4', 'Adenovirus τύπου 1'),
        ('ΕΜΒΟΛΙΟ_5', 'Parvovirus'),
        ('ΕΜΒΟΛΙΟ_6', 'Parainfluenza'),
    ]
    
    STERILIZATION_CHOICES = [
        ('yes', 'Ναι'),
        ('no', 'Όχι'),
        ('scheduled', 'Προγραμματισμένο'),
        ('unknown', 'Άγνωστη'),
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
    species = models.CharField(max_length=10, choices=SPECIES_CHOICES, verbose_name='Είδος')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name='Φύλο')
    
    # Age - either numeric age OR category
    age_numeric = models.PositiveIntegerField(
        verbose_name='Ηλικία (αριθμός)',
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(30)]
    )
    age_category = models.CharField(
        verbose_name='Κατηγορία Ηλικίας',
        max_length=15, 
        choices=AGE_CATEGORY_CHOICES,
        null=True, blank=True
    )
    
    name = models.CharField(max_length=20, verbose_name='Όνομα')
    
    # Shelter field
    shelter = models.CharField(
        max_length=100,
        default=get_default_shelter_name,
        verbose_name='Καταφύγιο'
    )
    
    # Rabies vaccination (mandatory by law)
    rabies_vaccinated = models.BooleanField(
        default=False,
        verbose_name='Εμβολιασμένο κατά Λύσσας'
    )
    rabies_vaccination_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Ημερομηνία Εμβολιασμού Λύσσας'
    )
     
    # Health and Behavior
    injured = models.BooleanField(default=False, verbose_name='Τραυματισμένο')
    behavior = models.CharField(max_length=25, choices=BEHAVIOR_CHOICES, verbose_name='Συμπεριφορά')
    vaccination_status = models.CharField(max_length=15, choices=VACCINATION_CHOICES, verbose_name='Κατάσταση Εμβολιασμού')
    sterilization_status = models.CharField(max_length=15, choices=STERILIZATION_CHOICES, verbose_name='Κατάσταση Στείρωσης')
    
    # Location and Housing
    cage_number = models.PositiveIntegerField(verbose_name='Αριθμός Κλουβιού', 
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    
    # Dates and Location
    entry_date = models.DateTimeField(auto_now_add=True)
    capture_location = models.CharField(max_length=100, verbose_name='Τοποθεσία Εύρεσης')
    capture_date = models.DateField(verbose_name='Ημερομηνία Εύρεσης')
    
    # Contact and Adoption
    finder_contact = models.TextField(blank=True, verbose_name='Στοιχεία του ευρέτη')
    public_visibility = models.BooleanField(default=False, verbose_name='Δημόσια προβολή')
    adoption_status = models.CharField(max_length=20, choices=ADOPTION_STATUS_CHOICES, default='available', verbose_name='Κατάσταση Υιοθεσίας')
    
    # QR Code
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True, verbose_name='QR Code')
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Δημιουργήθηκε από')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Δημιουργήθηκε στις')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ενημερώθηκε')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Ζώο"
        verbose_name_plural = "Ζώα"
    
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
        """Generate QR code data with configured domain"""
        # Read domain from environment variable with fallback
        domain = os.environ.get('DOMAIN', 'shelter.nafnaf.gr')
    
        return {
           "type": "animal_profile",
          "animal_id": self.pk,
          "chip_id": self.chip_id,
          "name": self.name,
          "species": self.get_species_display(),
          "gender": self.get_gender_display(),
          "cage": self.cage_number,
          "shelter": self.shelter,
          "entry_date": self.entry_date.isoformat(),
          "url": f"https://{domain}/adopt/{self.pk}",
          "api_url": f"https://{domain}/api/v1/animals/{self.pk}/"
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
    
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='medical_records', verbose_name='Ζώο')
    record_type = models.CharField(max_length=15, choices=RECORD_TYPE_CHOICES, verbose_name='Τύπος Αρχείου')
    description = models.TextField(max_length=300, verbose_name='Περιγραφή')
    date_recorded = models.DateField(verbose_name='Ημερομηνία Καταγραφής')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Δημιουργήθηκε από')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Δημιουργήθηκε στις')
    
    class Meta:
        ordering = ['-date_recorded']
        verbose_name = "Ιατρικό Αρχείο"
        verbose_name_plural = "Ιατρικά Αρχεία"
    
    def __str__(self):
        return f"{self.animal.name} - {self.get_record_type_display()}"


class AnimalPhoto(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='photos', verbose_name='Ζώο')
    image = models.ImageField(upload_to='animal_photos/', verbose_name='Εικόνα')
    is_primary = models.BooleanField(default=False, verbose_name='Κύρια Φωτογραφία')
    caption = models.CharField(max_length=100, blank=True, verbose_name='Λεζάντα')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Ανέβηκε στις')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Ανέβηκε από')
    
    class Meta:
        ordering = ["-is_primary", "-uploaded_at"]
        verbose_name = "Φωτογραφία Ζώου"
        verbose_name_plural = "Φωτογραφίες Ζώων"
    
    def __str__(self):
        return f"Photo of {self.animal.name}"


class Vaccination(models.Model):
    """Καταγραφή εμβολιασμών ζώων"""
    VACCINE_CHOICES = [
        ('dhppi', 'DHPPi'),
        ('dappi', 'DAPPi'),
        ('parainfluenza', 'Parainfluenza'),
        ('parvovirus', 'Parvovirus'),
        ('leptospirosis', 'Λεπτοσπείρωση'),
        ('other', 'Άλλο'),
    ] 
    
    animal = models.ForeignKey(
        Animal, 
        on_delete=models.CASCADE, 
        related_name='vaccinations',
        verbose_name='Ζώο'
    )
    vaccine_name = models.CharField(
        max_length=50, 
        choices=VACCINE_CHOICES, 
        verbose_name='Εμβόλιο'
    )
    other_vaccine_name = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name='Όνομα Εμβολίου (αν επιλέξατε Άλλο)'
    )
    date_administered = models.DateField(
        verbose_name='Ημερομηνία Χορήγησης'
    )
    next_due_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='Επόμενη Δόση'
    )
    administered_by = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name='Κτηνίατρος'
    )
    batch_number = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name='Αριθμός Παρτίδας'
    )
    notes = models.TextField(
        blank=True, 
        verbose_name='Σημειώσεις'
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name='Καταχωρήθηκε από'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Ημερομηνία Καταχώρησης'
    )
    
    class Meta:
        ordering = ['-date_administered']
        verbose_name = 'Εμβολιασμός'
        verbose_name_plural = 'Εμβολιασμοί'
    
    def __str__(self):
        vaccine_display = self.other_vaccine_name if self.vaccine_name == 'other' else self.get_vaccine_name_display()
        return f"{self.animal.name} - {vaccine_display} ({self.date_administered})"
    
    def get_vaccine_display_name(self):
        """Επιστρέφει το όνομα του εμβολίου για εμφάνιση"""
        if self.vaccine_name == 'other' and self.other_vaccine_name:
            return self.other_vaccine_name
        return self.get_vaccine_name_display()

# Force verbose_name_plural (workaround for caching issue)
Animal._meta.verbose_name_plural = "Ζώα"
MedicalRecord._meta.verbose_name_plural = "Ιατρικά Αρχεία"

# Force verbose_name (singular) for add buttons
Animal._meta.verbose_name = "Ζώο"
MedicalRecord._meta.verbose_name = "Ιατρικό Αρχείο"