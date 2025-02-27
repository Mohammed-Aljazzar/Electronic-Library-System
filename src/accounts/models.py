from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string

from project import settings

class Gender(models.TextChoices):
    MALE = 'M', 'Male'
    FEMALE = 'F', 'Female'
    OTHER = 'O', 'Other'

class CustomUser(AbstractUser):
    address = models.CharField(max_length=255)
    profession = models.CharField(max_length=100)
    residence = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    country_code = models.CharField(max_length=5)
    gender = models.CharField(max_length=1, choices=Gender.choices)
    profile_picture = models.ImageField(upload_to='profile_pictures/')
    can_add_books = models.BooleanField(default=False, verbose_name="Can Add Books")

    
    def str(self):
        return self.username
    
    # def generate_token(self):
    #     """Generate a random token for account deletion confirmation."""
    #     token = get_random_string(length=32)
    #     # Here, instead of storing in session, store it in cache or directly in the model if you don't mind persisting it.
    #     if hasattr(settings, 'CACHES'):
    #         from django.core.cache import cache
    #         cache.set(f"token_{self.pk}", token, timeout=3600)  # 1 hour expiry
    #     return token

    # def check_token(self, token):
    #     """Check if the provided token matches the one generated for this user."""
    #     if hasattr(settings, 'CACHES'):
    #         from django.core.cache import cache
    #         stored_token = cache.get(f"token_{self.pk}")
    #         return stored_token == token
    #     return False
