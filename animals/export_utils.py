"""Excel export utilities for animal shelter data"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from datetime import datetime
from django.http import HttpResponse


def generate_animals_excel(queryset):
    """Generate Excel file with 4 sheets: Animals, Medical Records, Vaccinations, Photos"""
    wb = Workbook()
    
    # Sheet 1: Animals
    ws_animals = wb.active
    ws_animals.title = "Ζώα"
    
    animal_headers = [
        'Chip ID', 'Όνομα', 'Είδος', 'Φύλο', 'Ηλικία', 'Συμπεριφορά',
        'Κατάσταση Εμβολιασμού', 'Στείρωση', 'Κλουβί', 'Τοποθεσία Εύρεσης',
        'Ημ/νία Εισαγωγής', 'Κατάσταση Υιοθεσίας', 'Δημόσια Προβολή',
        'Πλήθος Ιατρικών', 'Πλήθος Εμβολιασμών'
    ]
    ws_animals.append(animal_headers)
    
    # Style headers
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    for cell in ws_animals[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    ws_animals.freeze_panes = "A2"
    
    # Add animal data
    for animal in queryset:
        age_display = f"{animal.age_numeric}" if animal.age_numeric else animal.get_age_category_display() or "-"
        
        row = [
            animal.chip_id,
            animal.name,
            animal.get_species_display(),
            animal.get_gender_display(),
            age_display,
            animal.get_behavior_display(),
            animal.get_vaccination_status_display(),
            animal.get_sterilization_status_display(),
            animal.cage_number or "-",
            animal.capture_location or "-",
            animal.entry_date.strftime('%d/%m/%Y') if animal.entry_date else "-",
            animal.get_adoption_status_display(),
            "Ναι" if animal.public_visibility else "Όχι",
            animal.medical_records.count(),
            animal.vaccinations.count()
        ]
        ws_animals.append(row)
    
    # Auto-adjust column widths
    for column in ws_animals.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws_animals.column_dimensions[column_letter].width = adjusted_width
    
    # Sheet 2: Medical Records
    ws_medical = wb.create_sheet("Ιατρικά Αρχεία")
    medical_headers = ['Chip ID Ζώου', 'Όνομα Ζώου', 'Τύπος Αρχείου', 'Περιγραφή', 'Ημερομηνία', 'Δημιουργήθηκε από']
    ws_medical.append(medical_headers)
    
    for cell in ws_medical[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    ws_medical.freeze_panes = "A2"
    
    for animal in queryset:
        for record in animal.medical_records.all():
            row = [
                animal.chip_id,
                animal.name,
                record.get_record_type_display(),
                record.description,
                record.date_recorded.strftime('%d/%m/%Y'),
                record.created_by.username if record.created_by else "-"
            ]
            ws_medical.append(row)
    
    for column in ws_medical.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws_medical.column_dimensions[column_letter].width = adjusted_width
    
    # Sheet 3: Vaccinations
    ws_vacc = wb.create_sheet("Εμβολιασμοί")
    vacc_headers = ['Chip ID Ζώου', 'Όνομα Ζώου', 'Τύπος Εμβολίου', 'Ημερομηνία', 'Επόμενη Δόση', 'Χορηγήθηκε από', 'Αριθμός Παρτίδας']
    ws_vacc.append(vacc_headers)
    
    for cell in ws_vacc[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    ws_vacc.freeze_panes = "A2"
    
    for animal in queryset:
        for vacc in animal.vaccinations.all():
            row = [
                animal.chip_id,
                animal.name,
                vacc.get_vaccine_display_name(),
                vacc.date_administered.strftime('%d/%m/%Y'),
                vacc.next_due_date.strftime('%d/%m/%Y') if vacc.next_due_date else "-",
                vacc.administered_by or "-",
                vacc.batch_number or "-"
            ]
            ws_vacc.append(row)
    
    for column in ws_vacc.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws_vacc.column_dimensions[column_letter].width = adjusted_width
    
    # Sheet 4: Photos
    ws_photos = wb.create_sheet("Φωτογραφίες")
    photo_headers = ['Chip ID Ζώου', 'Όνομα Ζώου', 'Κύρια', 'Λεζάντα', 'Ανέβηκε στις', 'URL Φωτογραφίας']
    ws_photos.append(photo_headers)
    
    for cell in ws_photos[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    ws_photos.freeze_panes = "A2"
    
    for animal in queryset:
        for photo in animal.photos.all():
            row = [
                animal.chip_id,
                animal.name,
                "Ναι" if photo.is_primary else "Όχι",
                photo.caption or "-",
                photo.uploaded_at.strftime('%d/%m/%Y %H:%M'),
                photo.image.url if photo.image else "-"
            ]
            ws_photos.append(row)
    
    for column in ws_photos.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws_photos.column_dimensions[column_letter].width = adjusted_width
    
    # Create HTTP response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"Καταφύγιο_Ζώων_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    wb.save(response)
    return response
