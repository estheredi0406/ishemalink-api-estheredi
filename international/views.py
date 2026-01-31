from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import InternationalCargo
from .serializers import InternationalCargoSerializer

class CreateCargoView(generics.ListCreateAPIView):
    """
    API endpoint that allows Agents to create and list International Cargo.
    """
    serializer_class = InternationalCargoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return InternationalCargo.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)