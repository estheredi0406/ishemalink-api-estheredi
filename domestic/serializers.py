from rest_framework import serializers
from .models import Shipment, ShipmentLog

class ShipmentLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentLog
        fields = ['status', 'location', 'timestamp']

class ShipmentSerializer(serializers.ModelSerializer):
    # Include the logs (history) when viewing a shipment
    logs = ShipmentLogSerializer(many=True, read_only=True)
    
    class Meta:
        model = Shipment
        fields = ['id', 'tracking_number', 'current_status', 'origin', 'destination', 'logs']
        read_only_fields = ['tracking_number', 'owner', 'current_status']


from .models import Tariff # Update import at the top!

class TariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = ['zone', 'base_rate', 'weight_multiplier']