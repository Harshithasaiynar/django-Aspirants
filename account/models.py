from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils import timezone

from datetime import timedelta
import uuid
# Create your models here.

class CustomUser(AbstractUser):
    """
    Inheriting AbstractUser and adding two new fields.
    """
    ACCOUNT_CHOICES = [('jobseeker', 'Job Seeker'), ('recruiter', 'Recruiter')]
    account_type = models.CharField(max_length=15, choices=ACCOUNT_CHOICES)

    email_verified = models.BooleanField(default=False)

class UserEmailVerification(models.Model):
    """
    Model for storing email verification key.
    """
    user = models.OneToOneField(CustomUser, related_name='email_verification')
    is_valid_key = models.BooleanField(default=True)
    key = models.CharField(max_length=40, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """
        overriding save() of Model to automatically
        generate new key whenever Model is saved.
        """
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    def generate_key(self):
        """
        generating random alphanumeric key using uuid.
        """
        return uuid.uuid4().hex

    def __str__(self):
        return self.user.username