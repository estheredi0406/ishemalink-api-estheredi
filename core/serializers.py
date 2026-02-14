from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from datetime import datetime

User = get_user_model()

# --- TASK 1: Custom JWT Claims ---
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims for Task 1 & 4
        token['role'] = user.role  # Baking the role into the token
        token['username'] = user.username
        return token

# --- TASK 1: Session Login ---
class LoginSerializer(serializers.Serializer):
    """
    Serializer for Session-based login (Task 1).
    Used by SessionLoginView.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

# --- TASK 2: Registration & KYC ---
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'nid', 'role', 'password', 'assigned_sector']
        extra_kwargs = {
            'nid': {'required': False},
            'assigned_sector': {'required': False}
        }

    def validate_nid(self, value):
        """
        Task 2 Requirement: NID Algorithm check.
        Validate 16 digits and birth year consistency.
        """
        if not value.isdigit() or len(value) != 16:
            raise serializers.ValidationError("NID must be exactly 16 digits.")
        
        # Example Rwandan NID logic: Digits 2-5 represent birth year
        nid_birth_year = int(value[1:5])
        current_year = datetime.now().year
        
        if nid_birth_year < 1900 or nid_birth_year > current_year:
            raise serializers.ValidationError("Invalid birth year encoded in NID.")
            
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['phone'], 
            phone=validated_data['phone'],
            role=validated_data.get('role', 'CUSTOMER'),
            nid=validated_data.get('nid'),
            assigned_sector=validated_data.get('assigned_sector'),
            password=validated_data['password']
        )
        return user

# --- Identity & Recovery Serializers ---

class OTPRequestSerializer(serializers.Serializer):
    """ Just an empty serializer to trigger the button in Swagger """
    pass

class OTPVerifySerializer(serializers.Serializer):
    """ Accepts the 6-digit code for Task 2 verification """
    otp_code = serializers.CharField(max_length=6, min_length=6)

class NIDSubmitSerializer(serializers.Serializer):
    """ this accepts the 16-digit National ID for existing users """
    nid_number = serializers.CharField(max_length=16, min_length=16)

class NIDCheckSerializer(serializers.Serializer):
    """ Standalone check for NID format """
    nid = serializers.CharField(min_length=16, max_length=16)

class PasswordChangeSerializer(serializers.Serializer):
    """ his Authenticated password change """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)