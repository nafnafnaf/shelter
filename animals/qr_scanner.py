"""
QR Code Scanner functionality for animal shelter
Provides web-based QR scanning and API endpoints for QR lookup
"""
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Animal


def qr_scanner_page(request):
    """
    Web page with QR code scanner interface
    Accessible to anyone (staff and public)
    """
    return render(request, 'animals/qr_scanner.html')


@csrf_exempt
@require_http_methods(["POST"])
def scan_qr_code(request):
    """
    API endpoint to process scanned QR codes
    Receives QR data and returns animal information
    """
    try:
        data = json.loads(request.body)
        qr_data = data.get('qr_data', '')
        
        # Parse QR data (it should be JSON from our generated QR codes)
        try:
            qr_info = json.loads(qr_data)
            chip_id = qr_info.get('chip_id')
        except (json.JSONDecodeError, AttributeError):
            # If it's not JSON, assume it's just a chip_id string
            chip_id = qr_data.strip()
        
        if not chip_id:
            return JsonResponse({
                'success': False,
                'error': 'No chip ID found in QR code'
            }, status=400)
        
        # Look up the animal
        try:
            animal = Animal.objects.get(chip_id=chip_id)
            
            # Get primary photo or first photo
            photo = animal.photos.filter(is_primary=True).first() or animal.photos.first()
            photo_url = photo.image.url if photo else None
            
            response_data = {
                'success': True,
                'animal': {
                    'id': animal.id,
                    'chip_id': animal.chip_id,
                    'name': animal.name,
                    'species': animal.get_species_display(),
                    'gender': animal.get_gender_display(),
                    'age': animal.age_numeric if animal.age_numeric else animal.get_age_category_display(),
                    'cage_number': animal.cage_number,
                    'behavior': animal.get_behavior_display(),
                    'vaccination_status': animal.get_vaccination_status_display(),
                    'sterilization_status': animal.get_sterilization_status_display(),
                    'adoption_status': animal.get_adoption_status_display(),
                    'injured': animal.injured,
                    'photo_url': photo_url,
                    'public_url': f'/adopt/{animal.id}/' if animal.public_visibility else None,
                    'entry_date': animal.entry_date.strftime('%Y-%m-%d'),
                }
            }
            
            return JsonResponse(response_data)
            
        except Animal.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'Animal with chip ID {chip_id} not found'
            }, status=404)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def public_qr_lookup(request):
    """
    Public API endpoint to look up animal by chip_id
    Used by QR scanner and external services
    """
    chip_id = request.GET.get('chip_id', '').strip()
    
    if not chip_id:
        return JsonResponse({
            'success': False,
            'error': 'chip_id parameter required'
        }, status=400)
    
    try:
        animal = Animal.objects.get(chip_id=chip_id)
        
        # Only return public info for non-public animals
        if not animal.public_visibility:
            return JsonResponse({
                'success': True,
                'animal': {
                    'chip_id': animal.chip_id,
                    'name': animal.name,
                    'species': animal.get_species_display(),
                    'status': 'Registered in shelter system',
                    'message': 'Contact shelter for more information'
                }
            })
        
        # Return full public info for publicly visible animals
        photo = animal.photos.filter(is_primary=True).first() or animal.photos.first()
        photo_url = request.build_absolute_uri(photo.image.url) if photo else None
        
        return JsonResponse({
            'success': True,
            'animal': {
                'chip_id': animal.chip_id,
                'name': animal.name,
                'species': animal.get_species_display(),
                'gender': animal.get_gender_display(),
                'age': animal.age_numeric if animal.age_numeric else animal.get_age_category_display(),
                'adoption_status': animal.get_adoption_status_display(),
                'photo_url': photo_url,
                'public_url': request.build_absolute_uri(f'/adopt/{animal.id}/'),
            }
        })
        
    except Animal.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Animal not found'
        }, status=404)