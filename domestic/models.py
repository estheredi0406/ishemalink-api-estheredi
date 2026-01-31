from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string

class Shipment(models.Model):
    """
    Represents a package being moved within Rwanda.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_TRANSIT', 'In Transit'),
        ('DELIVERED', 'Delivered'),
        ('FAILED', 'Failed'),
    ]

    # Link to the Custom User we created in Task 2
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    tracking_number = models.CharField(max_length=20, unique=True, editable=False)
    current_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-generate a tracking number (e.g., RW-AB12CD) if it doesn't exist
        if not self.tracking_number:
            self.tracking_number = 'RW-' + get_random_string(8).upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tracking_number} ({self.current_status})"

class ShipmentLog(models.Model):
    """
    History of status updates.
    """
    shipment = models.ForeignKey(Shipment, related_name='logs', on_delete=models.CASCADE)
    status = models.CharField(max_length=20)
    location = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.shipment.tracking_number} - {self.status}"
    

class Tariff(models.Model):
    """
    Stores base rates for different zones.
    Rates rarely change, making them perfect candidates for caching.
    """
    ZONE_CHOICES = [
        ('ZONE1', 'Zone 1 - Kigali'),
        ('ZONE2', 'Zone 2 - Provinces'),
        ('ZONE3', 'Zone 3 - EAC (International)'),
    ]
    
    zone = models.CharField(max_length=10, choices=ZONE_CHOICES, unique=True)
    base_rate = models.DecimalField(max_digits=10, decimal_places=2)
    weight_multiplier = models.DecimalField(max_digits=5, decimal_places=2, help_text="Cost per extra kg")

    def __str__(self):
        return f"{self.zone}: {self.base_rate} RWF"