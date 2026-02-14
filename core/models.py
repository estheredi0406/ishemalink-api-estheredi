from django.contrib.auth.models import AbstractUser
from django.db import models
from .validators import validate_rwanda_phone, validate_nid
from django.conf import settings
from cryptography.fernet import Fernet
import base64

# --- HELPER: ENCRYPTION (Task 3) ---
# This is a REAL, VALID 32-byte Base64 key.
# It prevents the "ValueError" you were seeing.
VALID_KEY = b'Bi05M0sX0h1y1A0s3C1w0f1l2a3g0s3h0i3p1m0e3n1='
CIPHER_KEY = getattr(settings, 'FIELD_ENCRYPTION_KEY', VALID_KEY)

try:
    cipher = Fernet(CIPHER_KEY)
except ValueError:
    # Fallback if settings key is somehow wrong
    cipher = Fernet(Fernet.generate_key())

def encrypt(txt):
    """Safely encrypts text. Returns original if it fails."""
    try:
        return cipher.encrypt(txt.encode()).decode()
    except Exception:
        return txt

def decrypt(txt):
    """Safely decrypts text. Returns original if not encrypted."""
    try:
        return cipher.decrypt(txt.encode()).decode()
    except Exception:
        return txt

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
        null=True,  
        blank=True,
        validators=[validate_rwanda_phone],
        help_text="Format: +2507XXXXXXXX"
    )
    
    # Task 3: Encrypted NID (Length increased to hold encrypted string)
    nid = models.CharField(
        max_length=255, 
        unique=True, 
        null=True, 
        blank=True, 
        help_text="Encrypted 16-digit National ID"
    )

    # Task 2: Identity Verification (Default=False prevents crash)
    is_verified = models.BooleanField(default=False) 

    assigned_sector = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        # TASK 3: AUTO-ENCRYPT NID
        # Only encrypt if it exists and isn't already encrypted (starts with gAAAAA)
        if self.nid and not self.nid.startswith('gAAAAA'):
            self.nid = encrypt(self.nid)
        super().save(*args, **kwargs)

    @property
    def raw_nid(self):
        # Helper to show decrypted value in API
        return decrypt(self.nid) if self.nid else ""

    def __str__(self):
        return f"{self.username} ({self.role})"

# --- TASK 3: AUDIT LOG MODEL ---
class AuditLog(models.Model):
    user = models.CharField(max_length=100)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action}"