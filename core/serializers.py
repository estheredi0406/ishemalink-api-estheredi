from rest_framework import serializers
from django.contrib.auth import get_user_model
from .validators import validate_nid

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for registering new agents/customers.
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'nid', 'role', 'password', 'assigned_sector']
        extra_kwargs = {
            'nid': {'required': False},
            'assigned_sector': {'required': False}
        }

    def create(self, validated_data):
        # We use the phone number as the username for simplicity
        user = User.objects.create_user(
            username=validated_data['phone'], 
            phone=validated_data['phone'],
            role=validated_data.get('role', 'CUSTOMER'),
            nid=validated_data.get('nid'),
            assigned_sector=validated_data.get('assigned_sector'),
            password=validated_data['password']
        )
        return user

class NIDCheckSerializer(serializers.Serializer):
    """
    Simple serializer to validate NID format without creating a user.
    """
    nid = serializers.CharField(min_length=16, max_length=16)