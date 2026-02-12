from django.test import TestCase
from django.core.exceptions import ValidationError
from .validators import validate_rwanda_phone, validate_nid

class ValidatorTests(TestCase):
    """
    Automated tests to prove Identity Validation works correctly.
    """

    # --- Phone Number Tests ---
    def test_valid_rwanda_phone(self):
        """Test that a correct +250 number passes."""
        try:
            validate_rwanda_phone("+250788123456")
        except ValidationError:
            self.fail("validate_rwanda_phone raised ValidationError unexpectedly!")

    def test_invalid_phone_prefix(self):
        """Test that a number without +250 fails."""
        with self.assertRaises(ValidationError):
            validate_rwanda_phone("0788123456")

    def test_phone_too_short(self):
        """Test that a short number fails."""
        with self.assertRaises(ValidationError):
            validate_rwanda_phone("+250788")

    # --- National ID Tests ---
    def test_valid_nid(self):
        """Test that a 16-digit NID passes."""
        try:
            validate_nid("1199080012345678")
        except ValidationError:
            self.fail("validate_nid raised ValidationError unexpectedly!")

    def test_nid_too_short(self):
        """Test that a 5-digit NID fails."""
        with self.assertRaises(ValidationError):
            validate_nid("12345")

    def test_nid_not_numeric(self):
        """Test that an NID with letters fails."""
        with self.assertRaises(ValidationError):
            validate_nid("11990800ABCD5678")