import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shelter_registry.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.admin.sites import site
from django.contrib.auth import get_user_model
from animals.models import MedicalRecord
from django_tenants.utils import schema_context
from django.db import connection

# Simulate a real request through middleware
from shelter.models import Domain
domain = Domain.objects.get(domain='shelter.nafnaf.gr')
connection.tenant = domain.tenant

print(f"Tenant set to: {connection.tenant.schema_name}")

# Create request
factory = RequestFactory()
request = factory.get('/admin/animals/medicalrecord/', HTTP_HOST='shelter.nafnaf.gr')

with schema_context('myshelter'):
    User = get_user_model()
    request.user = User.objects.filter(is_superuser=True).first()

# Get admin class
admin_class = site._registry[MedicalRecord]

print(f"Calling changelist_view...")

# Call changelist_view (which should now use schema_context internally)
try:
    response = admin_class.changelist_view(request)
    print(f"Response type: {type(response)}")
    print(f"Response status: {response.status_code}")
    
    # Render it
    if hasattr(response, 'render'):
        response.render()
        print(f"Content length: {len(response.content)} bytes")
        if len(response.content) > 0:
            print(f"SUCCESS! First 300 chars:\n{response.content[:300]}")
        else:
            print("STILL EMPTY!")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
