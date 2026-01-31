from django.db import models
from django.conf import settings

class InternationalCargo(models.Model):
    """
    Represents heavy cargo moving across borders (EAC Trade).
    Distinct from Domestic Shipment because it requires Trade Docs.
    """
    DESTINATION_CHOICES = [
        ('UG', 'Uganda'),
        ('KE', 'Kenya'),
        ('TZ', 'Tanzania'),
        ('CD', 'DRC'),
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    manifest_id = models.CharField(max_length=50, unique=True, help_text="Customs Declaration Number")
    
    # These fields are unique to International Logic
    tin_number = models.CharField(max_length=20, help_text="Tax ID for trade")
    passport_number = models.CharField(max_length=20, blank=True, null=True)
    
    destination_country = models.CharField(max_length=2, choices=DESTINATION_CHOICES)
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2)
    
    is_customs_cleared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.manifest_id} -> {self.destination_country}"