from django.contrib import admin
from django.utils.html import format_html
from .export_utils import generate_animals_excel
from django.urls import reverse
from .models import Animal, MedicalRecord, AnimalPhoto, Vaccination
from .export_utils import export_animals_to_excel, export_vaccinations_to_excel
class MedicalRecordInline(admin.TabularInline):
    model = MedicalRecord
    extra = 1

class AnimalPhotoInline(admin.TabularInline):
    model = AnimalPhoto
    extra = 1
    fields = ['image', 'is_primary', 'caption']
    readonly_fields = []

class VaccinationInline(admin.StackedInline):
    model = Vaccination
    extra = 1
    fields =['vaccine_name', 'other_vaccine_name', 'batch_number', 'date_administered', 'administered_by'] 
    verbose_name = "Εμβολιασμός"
    verbose_name_plural = "Εμβολιασμοί"
    
    class Media:
        css = {
            'all': ('animals/css/vaccination_inline.css?v=3',)
        }
    
    def get_formset(self, request, obj=None, **kwargs):
        """Customize formset to make saved vaccinations readonly and show date in header"""
        formset = super().get_formset(request, obj, **kwargs)
        
        # Shorten field labels
        formset.form.base_fields['vaccine_name'].label = 'Εμβόλιο'
        formset.form.base_fields['other_vaccine_name'].label = 'Σκεύασμα'
        formset.form.base_fields['batch_number'].label = 'Αρ. Παρτίδας'
        formset.form.base_fields['date_administered'].label = 'Ημ/νια'
        formset.form.base_fields['administered_by'].label = 'Κτηνίατρος'
        
        # Override the formset's __init__ to set readonly on existing instances
        original_init = formset.__init__
        
        def custom_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            for form in self.forms:
                if form.instance.pk:  # Existing vaccination
                    for field_name in ['vaccine_name', 'other_vaccine_name', 'batch_number', 'date_administered', 'administered_by']: 
                        if field_name in form.fields:
                            form.fields[field_name].disabled = True
        
        formset.__init__ = custom_init
        return formset
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of vaccination records"""
        return False
@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    actions =['export_selected_to_excel', 'export_all_to_excel', 'regenerate_qr_codes', 'make_public', 'make_private']
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            actions['delete_selected'][0].short_description = "Διαγραφή επιλεγμένων"
        return actions
    
    list_display = ['photo_display', 'name', 'chip_id', 'species', 'gender', 'age_display', 'behavior', 'adoption_status', 'public_visibility', 'qr_code_display']
    list_filter = ['species', 'gender', 'behavior', 'adoption_status', 'public_visibility', 'sterilization_status', 'shelter']
    search_fields = ['name', 'chip_id', 'capture_location', 'shelter']
    inlines = [VaccinationInline, MedicalRecordInline, AnimalPhotoInline]
    readonly_fields = ['created_by', 'created_at', 'updated_at', 'entry_date', 'qr_code_preview']
    
    fieldsets = (
        ('Βασικές Πληροφορίες', {
            'fields': ('chip_id', 'name', 'species', 'gender', 'shelter')
        }),
        ('Πληροφορίες Ηλικίας', {
            'fields': ('age_numeric', 'age_category'),
            'description': 'Παρέχετε είτε αριθμητική ηλικία ΕΊΤΕ κατηγορία ηλικίας, όχι και τα δύο.'
        }),
        ('Υγεία & Συμπεριφορά', {
            'fields': ('injured', 'behavior',  'sterilization_status')
        }),
        ('Τοποθεσία & Στέγαση', {
            'fields': ('cage_number', 'capture_location', 'capture_date')
        }),
        ('Επικοινωνία & Υιοθεσία', {
            'fields': ('finder_contact', 'adoption_status', 'public_visibility')
        }),
        ('QR Code', {
            'fields': ('qr_code', 'qr_code_preview'),
            'classes': ('collapse',)
        }),
        ('Μεταδεδομένα', {
            'fields': ('created_by', 'created_at', 'updated_at', 'entry_date'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """
        Make chip_id readonly when editing existing animal.
        """
        readonly = list(self.readonly_fields)
        if obj:
            readonly.append('chip_id')
        return readonly
    
    def photo_display(self, obj):
        """Display animal's primary photo or first available photo as thumbnail"""
        photo = obj.photos.filter(is_primary=True).first() or obj.photos.first()
        
        if photo and photo.image:
            return format_html(
                '<img src="{}" width="60" height="60" style="object-fit: cover; border-radius: 4px; border: 1px solid #ccc;" title="{}"/>',
                photo.image.url,
                obj.name
            )
        return format_html('<span style="color: #999;">📷 No photo</span>')
    
    photo_display.short_description = 'Φωτογραφία'
    
    def changelist_view(self, request, extra_context=None):
        """Override to add statistics to the changelist page"""
        from django.db.models import Count, Q
        
        stats = {
            'total': Animal.objects.count(),
            'dogs': Animal.objects.filter(species='dog').count(),
            'cats': Animal.objects.filter(species='cat').count(),
            'other_species': Animal.objects.filter(species='other').count(),
            'males': Animal.objects.filter(gender='male').count(),
            'females': Animal.objects.filter(gender='female').count(),
            'sterilized': Animal.objects.filter(sterilization_status='yes').count(),
            'not_sterilized': Animal.objects.filter(sterilization_status='no').count(),
            'sterilization_scheduled': Animal.objects.filter(sterilization_status='scheduled').count(),
            'injured': Animal.objects.filter(injured=True).count(),
            'healthy': Animal.objects.filter(injured=False).count(),
            'available': Animal.objects.filter(adoption_status='available').count(),
            'pending': Animal.objects.filter(adoption_status='pending').count(),
            'adopted': Animal.objects.filter(adoption_status='adopted').count(),
            'not_for_adoption': Animal.objects.filter(adoption_status='not_for_adoption').count(),
            'public': Animal.objects.filter(public_visibility=True).count(),
            'private': Animal.objects.filter(public_visibility=False).count(),
        }
        
        extra_context = extra_context or {}
        extra_context['stats'] = stats
        return super().changelist_view(request, extra_context=extra_context)
    
    def age_display(self, obj):
        if obj.age_numeric:
            return f"{obj.age_numeric} έτη"
        elif obj.age_category:
            return obj.get_age_category_display()
        return "Μη καθορισμένη"
    age_display.short_description = 'Ηλικία'
    
    def qr_code_display(self, obj):
        if obj.qr_code:
            return format_html(
                '<img src="{}" width="50" height="50" style="border: 1px solid #ccc;" title="QR Code"/>',
                obj.qr_code.url
            )
        return "No QR"
    qr_code_display.short_description = 'QR Code'
    
    def qr_code_preview(self, obj):
        if obj.qr_code:
            return format_html(
                '<div>'
                '<img src="{}" width="200" height="200" style="border: 1px solid #ccc;"/>'
                '<br/><br/>'
                '<strong>QR Data:</strong><br/>'
                '<pre style="background: #f5f5f5; padding: 10px; font-size: 11px;">{}</pre>'
                '<br/>'
                '<a href="{}" target="_blank" class="button">View Full Size</a> '
                '<button type="button" onclick="regenerateQR({})" class="button">Regenerate QR</button>'
                '</div>',
                obj.qr_code.url,
                format(obj.get_qr_data()),
                obj.qr_code.url,
                obj.pk
            )
        return "QR code will be generated automatically when you save this animal."
    qr_code_preview.short_description = 'QR Code Preview'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def save_formset(self, request, form, formset, change):
        """
        Override to prevent chip_id validation errors when saving inline photos/medical records.
        This is a known Django issue where inline formsets re-validate parent model's unique fields.
        """
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if not instance.pk:
                if hasattr(instance, 'uploaded_by'):
                    instance.uploaded_by = request.user
                elif hasattr(instance, 'created_by'):
                    instance.created_by = request.user
            instance.save()
        formset.save_m2m()
    
    def regenerate_qr_codes(self, request, queryset):
        """Admin action to regenerate QR codes for selected animals"""
        count = 0
        for animal in queryset:
            if animal.qr_code:
                animal.qr_code.delete(save=False)
            animal.generate_qr_code()
            animal.save(update_fields=['qr_code'])
            count += 1
        
        self.message_user(request, f'Successfully regenerated QR codes for {count} animals.')
    regenerate_qr_codes.short_description = 'Αναδημιουργία QR codes για επιλεγμένα ζώα'
    
    def make_public(self, request, queryset):
        """Admin action to make animals publicly visible"""
        count = queryset.update(public_visibility=True)
        self.message_user(request, f'Successfully made {count} animals publicly visible.')
    make_public.short_description = 'Δημόσια προβολή επιλεγμένων ζώων'
    
    def make_private(self, request, queryset):
        """Admin action to make animals private"""
        count = queryset.update(public_visibility=False)
        self.message_user(request, f'Successfully made {count} animals private.')
    make_private.short_description = 'Απόκρυψη επιλεγμένων ζώων από το κοινό'
    def export_selected_to_excel(self, request, queryset):
        """Export selected animals to Excel"""
        return export_animals_to_excel(queryset)
    export_selected_to_excel.short_description = 'Εξαγωγή επιλεγμένων σε Excel'
    
    def export_all_to_excel(self, request, queryset):
        """Export all animals (respecting current filters) to Excel"""
        # Get all animals with current filters applied
        all_animals = self.get_queryset(request)
        return export_animals_to_excel(all_animals)
    export_all_to_excel.short_description = 'Εξαγωγή όλων σε Excel (με φίλτρα)'

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['animal', 'record_type', 'date_recorded', 'created_by']
    list_filter = ['record_type', 'date_recorded']
    search_fields = ['animal__name', 'animal__chip_id', 'description']
    readonly_fields = ['created_by', 'created_at']
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
      

@admin.register(Vaccination)
class VaccinationAdmin(admin.ModelAdmin):
    list_display = ['animal', 'vaccine_name', 'date_administered', 'next_due_date', 'administered_by', 'created_by']
    list_filter = ['vaccine_name', 'date_administered']
    search_fields = ['animal__name', 'animal__chip_id', 'administered_by']
    readonly_fields = ['created_by', 'created_at']
    
    def get_queryset(self, request):
        """Show rabies vaccinations first"""
        qs = super().get_queryset(request)
        return qs.extra(select={'is_rabies': "CASE WHEN vaccine_name = 'rabies' THEN 0 ELSE 1 END"}).order_by('is_rabies', '-date_administered')
    
    def get_readonly_fields(self, request, obj=None):
        """
        Make date_administered readonly after save (prevent modification)
        """
        readonly = list(self.readonly_fields)
        if obj:  # Editing existing vaccination
            readonly.append('date_administered')
        return readonly
    
    def has_delete_permission(self, request, obj=None):
        """
        Prevent deletion of all vaccination records
        """
        return False
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(AnimalPhoto)
class AnimalPhotoAdmin(admin.ModelAdmin):
    list_display = ['animal', 'is_primary', 'caption', 'uploaded_at', 'image_preview']
    list_filter = ['is_primary', 'uploaded_at']
    search_fields = ['animal__name', 'animal__chip_id', 'caption']
    readonly_fields = ['uploaded_by', 'uploaded_at', 'image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover; border: 1px solid #ccc;"/>',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Προεπισκόπηση'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


# Customize admin site header and title
from django.contrib import admin as admin_module
from .version import get_version
import os

VERSION = get_version()
ORGANIZATION_NAME = os.environ.get('ORGANIZATION_NAME', 'Καταφύγιο Ζώων')

admin_module.site.site_header = f"{ORGANIZATION_NAME} - {VERSION}"
admin_module.site.site_title = "Καταφύγιο Ζώων"
admin_module.site.index_title = "Διαχείριση Ζώων"