from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from account.validators import phone_validator
from account.managers import CustomUserManager


class CustomUser(AbstractUser):
    phone_number = models.CharField(
        max_length=11, unique=True, validators=[phone_validator,]
    )
    address = models.TextField(null=True, blank=True)
    is_phone_verified = models.BooleanField(default=False)
    username = None

    objects = CustomUserManager()

    USERNAME_FIELD = "phone_number"

    def __str__(self) -> str:
        return self.get_full_name()


class OTP(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='otp')
    secret = models.CharField(max_length=100)
    request_time = models.DateTimeField(auto_now=True)
