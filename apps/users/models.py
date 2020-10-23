from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from rest_framework.authtoken.models import Token

from apps.core.models import AbstractBaseModel


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=self.normalize_email(email),
        )
        if password is not None:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def create_superuser(self, username, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.username = username
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        return user


class User(AbstractUser, AbstractBaseModel):
    ROLE_CHOICES = (
        (1, 'Patient'),
        (2, 'Dietitian'),
        (3, 'Kitchen'),
        (4, 'Nurse'),
        (5, 'Agent'),
        (6, 'Manager')
    )
    ERA_CHOICES = (
        (True, 'T'),
        (False, 'S')
    )
    GENDER_CHOICES = (
        (True, 'Male'),
        (False, 'Female')
    )
    UNIT_DIRECTION_CHOICES = (
        (True, 'North'),
        (False, 'South')
    )
    # Common
    salutarium = models.ForeignKey("property.Salutarium", on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(blank=True, null=True, max_length=255, )
    email = models.EmailField( unique=True, blank=False, null=False)
    password = models.CharField(_('password'), max_length=128, null=True, blank=True)
    reset_key = models.CharField(blank=True, null=True, max_length=255)
    role = models.IntegerField(choices=ROLE_CHOICES, blank=True, null=True)

    # For Patient
    birthday = models.DateField(blank=True, null=True)
    gender = models.BooleanField(choices=GENDER_CHOICES, default=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    unit_layer = models.CharField(blank=True, null=True, max_length=255)
    weight = models.FloatField(blank=True,  null=True)
    height = models.FloatField(blank=True, null=True)
    disease = models.CharField(blank=True, null=True, max_length=255, )
    contact = models.CharField(blank=True, null=True, max_length=20)
    money = models.FloatField(blank=True, null=True)

    # For Dietitian
    emergency_contact = models.CharField(blank=True, null=True, max_length=20)

    # For Kitchen
    company = models.CharField(blank=True, null=True, max_length=255)
    address = models.CharField(blank=True, null=True, max_length=255, )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name_plural = 'User'

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)