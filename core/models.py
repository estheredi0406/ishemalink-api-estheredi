from django.contrib.auth.models import AbstractUser
from django.db import models
from .validators import validate_rwanda_phone, validate_nid
from django.conf import settings
from cryptography.fernet import Fernet
import os

# --- HELPER: ENCRYPTION UTILS ---
VALID_KEY = b'Bi05M0sX0h1y1A0s3C1w0f1l2a3g0s3h0i3p1m0e3n1='
CIPHER_KEY = getattr(settings, 'FIELD_ENCRYPTION_KEY', VALID_KEY)
cipher = Fernet(CIPHER_KEY)

def encrypt(txt):
    if not txt: return None
    return cipher.encrypt(str(txt).encode()).decode()

def decrypt(txt):
    if not txt: return None
    try:
        return cipher.decrypt(txt.encode()).decode()
    except Exception:
        return txt

# --- USER MODEL WITH LOGISTICS HIERARCHY (Task 4) ---
class User(AbstractUser):
    class Roles(models.TextChoices):
        CUSTOMER = 'CUSTOMER', 'Customer'
        DRIVER = 'DRIVER', 'Truck Driver'     # New for Task 4
        AGENT = 'AGENT', 'Sector Agent'
        GOV = 'GOV', 'RURA/RRA Inspector'    # New for Task 4
        ADMIN = 'ADMIN', 'System Admin'

    role = models.CharField(max_length=10, choices=Roles.choices, default=Roles.CUSTOMER)
    phone = models.CharField(max_length=13, unique=True, null=True, blank=True, validators=[validate_rwanda_phone])
    is_verified = models.BooleanField(default=False)
    assigned_sector = models.CharField(max_length=100, blank=True, null=True)
    consent_version = models.CharField(max_length=10, default="v1.0")
    consent_date = models.DateTimeField(auto_now_add=True)
    
    # Task 3: Encrypted Fields
    nid = models.CharField(max_length=255, unique=True, null=True, blank=True)
    tax_id = models.CharField(max_length=255, null=True, blank=True) # Added for Task 3 requirement
    
    def save(self, *args, **kwargs):
        # Auto-Encrypt NID and Tax ID
        if self.nid and not self.nid.startswith('gAAAAA'):
            self.nid = encrypt(self.nid)
        if self.tax_id and not self.tax_id.startswith('gAAAAA'):
            self.tax_id = encrypt(self.tax_id)
        super().save(*args, **kwargs)

    @property
    def decrypted_nid(self):
        return decrypt(self.nid)

# --- AUDIT LOG (Task 3 & 4) ---
class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    details = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} @ {self.timestamp}"

# --- SHIPMENT MODEL (Task 4 Logic) ---
class Shipment(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipments')
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='deliveries')
    destination = models.CharField(max_length=255)
    sector = models.CharField(max_length=100) # For Agent-level filtering
    cargo_value = models.CharField(max_length=255) # This will be encrypted!
    status = models.CharField(max_length=50, default='Pending')

    def save(self, *args, **kwargs):
        if not self.cargo_value.startswith('gAAAAA'):
            self.cargo_value = encrypt(self.cargo_value)
        super().save(*args, **kwargs)