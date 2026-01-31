from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from asgiref.sync import sync_to_async # <--- THE KEY TOOL
from drf_spectacular.utils import extend_schema

from .models import Shipment, ShipmentLog
from .serializers import ShipmentSerializer
from .utils import send_sms_notification


from rest_framework.generics import ListAPIView
from django.db.models import Q # Needed for search logic

class CreateShipmentView(generics.CreateAPIView):
    """
    Standard sync view to create a new shipment.
    """
    serializer_class = ShipmentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Auto-assign the logged-in user as the owner
        serializer.save(owner=self.request.user)

@extend_schema(
    request=None,
    responses={200: None},
    description="Updates status and sends async SMS (Non-blocking)."
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def update_shipment_status(request, pk):
    """
    Async view to handle status updates.
    It updates the DB (wrapped in sync_to_async) and then awaits the fake SMS.
    """
    try:
        # 1. Fetch Shipment (Database access must be wrapped)
        # We wrap get_object_or_404 to make it async-compatible
        shipment = await sync_to_async(get_object_or_404)(Shipment, pk=pk)

        # 2. Update Status (DB Write)
        new_status = request.data.get('status')
        location = request.data.get('location', 'Unknown Location')
        
        if new_status not in ['PENDING', 'IN_TRANSIT', 'DELIVERED', 'FAILED']:
            return Response({"error": "Invalid status"}, status=400)

        shipment.current_status = new_status
        await sync_to_async(shipment.save)() # Save Shipment

        # 3. Create Log Entry (DB Write)
        await sync_to_async(ShipmentLog.objects.create)(
            shipment=shipment,
            status=new_status,
            location=location
        )

        # 4. The Async Magic: Send SMS without blocking
        # This await releases the server to handle other requests while "waiting" for the SMS
        phone = await sync_to_async(lambda: shipment.owner.phone)()
        await send_sms_notification(phone, f"Your package is now {new_status} at {location}")

        return Response({"message": "Status updated and SMS queued."}, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
    

class ShipmentListView(ListAPIView):
    """
    GET /api/domestic/shipments/list/
    Returns a paginated list of shipments.
    Supports filtering by status and searching by tracking number.
    """
    serializer_class = ShipmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Custom logic to handle filtering and searching.
        """
        # Start with all shipments
        queryset = Shipment.objects.all().order_by('-created_at')

        # 1. FILTERING: Check if 'status' is in the URL (e.g., ?status=IN_TRANSIT)
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(current_status=status_param)

        # 2. FILTERING: Check if 'destination' is in the URL
        destination_param = self.request.query_params.get('destination')
        if destination_param:
            queryset = queryset.filter(destination__icontains=destination_param)

        # 3. SEARCHING: Check if 'search' is in the URL (e.g., ?search=RW-123)
        search_param = self.request.query_params.get('search')
        if search_param:
            queryset = queryset.filter(
                Q(tracking_number__icontains=search_param) | 
                Q(origin__icontains=search_param) |
                Q(destination__icontains=search_param)
            )

        return queryset