from rest_framework import serializers
from .models import InternationalCargo

class InternationalCargoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternationalCargo
        fields = '__all__'
        read_only_fields = ['owner', 'is_customs_cleared']

    def validate(self, data):
        """
        Cross-border rule: If destination is Kenya (KE), TIN is MANDATORY.
        """
        if data.get('destination_country') == 'KE' and not data.get('tin_number'):
            raise serializers.ValidationError("Shipments to Kenya require a valid TIN Number.")
        return data