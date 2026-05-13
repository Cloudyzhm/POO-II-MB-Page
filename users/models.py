from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('user_type', 'company')
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    USER_TYPES = [
        ('passenger', 'Pasajero'),
        ('driver', 'Conductor'),
        ('company', 'Empresa'),
        ('admin', 'Administrador'),
    ]
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='passenger')

    objects = UserManager()

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
