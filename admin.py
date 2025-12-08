from django.contrib import admin
from django_tenants.admin import TenantAdminMixin
from .models import Shelter, Domain, ShelterUser

@admin.register(Shelter)
class ShelterAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'schema_name', 'contact_email', 'created_on']
    search_fields = ['name', 'contact_email', 'schema_name']
    readonly_fields = ['schema_name', 'created_on']

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ['domain', 'tenant', 'is_primary']
    list_filter = ['is_primary']
    search_fields = ['domain', 'tenant__name']

@admin.register(ShelterUser)
class ShelterUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'user__email']