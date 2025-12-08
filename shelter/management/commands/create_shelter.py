from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shelter.models import Shelter, Domain, ShelterUser

class Command(BaseCommand):
    help = 'Create a new shelter with domain and admin user'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, required=True, help='Shelter name')
        parser.add_argument('--domain', type=str, required=True, help='Domain name (e.g., myshelter.localhost)')
        parser.add_argument('--email', type=str, required=True, help='Shelter contact email')
        parser.add_argument('--admin-username', type=str, required=True, help='Admin username')
        parser.add_argument('--admin-password', type=str, required=True, help='Admin password')
        parser.add_argument('--admin-email', type=str, required=True, help='Admin email')

    def handle(self, *args, **options):
        # Create shelter
        shelter = Shelter(
            schema_name=options['domain'].replace('.', '_').replace('-', '_'),
            name=options['name'],
            contact_email=options['email'],
        )
        shelter.save()
        
        # Create domain
        domain = Domain(
            domain=options['domain'],
            tenant=shelter,
            is_primary=True
        )
        domain.save()
        
        # Create admin user
        user = User.objects.create_user(
            username=options['admin_username'],
            email=options['admin_email'],
            password=options['admin_password']
        )
        
        # Create shelter user with admin role
        shelter_user = ShelterUser.objects.create(
            user=user,
            role='admin'
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created shelter "{options["name"]}" '
                f'with domain "{options["domain"]}" '
                f'and admin user "{options["admin_username"]}"'
            )
        )