from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a superuser with custom role'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username for the superuser')
        parser.add_argument('--email', type=str, help='Email for the superuser')
        parser.add_argument('--password', type=str, help='Password for the superuser')
        parser.add_argument('--role', type=str, default='superuser', 
                          choices=['superuser', 'exchange_admin', 'exchange_manager'],
                          help='Role for the user')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        role = options['role']

        if not all([username, email, password]):
            self.stdout.write(
                self.style.ERROR('Username, email, and password are required')
            )
            return

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role=role,
                is_staff=True,
                is_superuser=True if role == 'superuser' else False
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {role}: {username}')
            )
            
        except IntegrityError:
            self.stdout.write(
                self.style.ERROR(f'User with username "{username}" already exists')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating user: {str(e)}')
            )
