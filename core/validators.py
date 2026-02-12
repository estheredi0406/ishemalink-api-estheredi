import re
from django.core.exceptions import ValidationError

def validate_rwanda_phone(value: str) -> None:
    pattern = r"^\+2507[2389]\d{7}$"
    if not re.match(pattern, value):
        raise ValidationError("Sorry, but tour Phone number must be in the format +2507XXXXXXXX.")

def validate_nid(value: str) -> None:
    if not value.isdigit() or len(value) != 16:
        raise ValidationError("National ID must be exactly 16 numeric digits.")
    if not value.startswith("1"):
        raise ValidationError("Invalid National ID ormat.")