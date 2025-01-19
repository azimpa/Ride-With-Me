from django.contrib.auth.models import AbstractUser, Permission
from django.db import models
from decimal import Decimal
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    age = models.PositiveIntegerField()

    USERNAME_FIELD = 'username'

    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_user_permissions',
    )

    wallet_balance = models.DecimalField(max_digits=10,decimal_places=2,default=Decimal('0.00'),help_text='Wallet balance in user account.')
