from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('superuser', 'مدیر کل (SuperUser)'),
        ('exchange_admin', 'ادمین صرافی'),
        ('exchange_manager', 'مدیریت صرافی'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='exchange_manager')

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"
