from django.contrib.auth.models import AbstractUser
from django.db import models
from .validators import validate_rwanda_phone, validate_nid

class User(AbstractUser):
    """
    Custom User model supporting Agents, Customers, and Admins.
    """
    class Roles(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        AGENT = 'AGENT', 'Agent'
        CUSTOMER = 'CUSTOMER', 'Customer'

    role = models.CharField(
        max_length=10, 
        choices=Roles.choices, 
        default=Roles.CUSTOMER
    ) 

    phone = models.CharField(
        max_length=13, 
        unique=True, 
        validators=[validate_rwanda_phone],
        help_text="Format: +2507XXXXXXXX"
    )
    
    nid = models.CharField(
        max_length=16, 
        unique=True, 
        null=True, 
        blank=True, 
        validators=[validate_nid],
        help_text="16-digit National ID"
    )

    assigned_sector = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"