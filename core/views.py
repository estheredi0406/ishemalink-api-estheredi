from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema  # Required for doc fix

from .serializers import UserRegistrationSerializer, NIDCheckSerializer
from .validators import validate_nid

class RegisterUserView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    Registers a new user (Agent or Customer).
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny] 

class NIDVerifyView(APIView):
    """
    POST /api/auth/verify-nid/
    Standalone check for NID validity.
    """
    permission_classes = [AllowAny]

    # This decorator tells Swagger what data to expect, fixing the warning
    @extend_schema(
        request=NIDCheckSerializer,
        responses={200: NIDCheckSerializer},
        description="Validates a 16-digit Rwanda National ID."
    )
    def post(self, request):
        serializer = NIDCheckSerializer(data=request.data)
        if serializer.is_valid():
            nid = serializer.validated_data['nid']
            try:
                # Re-use our logic from validators.py
                validate_nid(nid)
                return Response({"valid": True, "nid": nid}, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response({"valid": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)