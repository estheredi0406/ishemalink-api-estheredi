from rest_framework import views, generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import AnonRateThrottle
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsGovOfficial, IsSectorAgent
from .serializers import ShipmentSerializer
from .models import Shipment

# Internal Imports
from .utils import generate_otp, verify_otp_logic
from .validators import validate_nid
from .models import AuditLog # Task 3 requirement

# --- Imports: Serializers ---
try:
    from .serializers import (
        UserRegistrationSerializer, 
        NIDCheckSerializer, 
        LoginSerializer,
        OTPVerifySerializer, 
        NIDSubmitSerializer  
    )
except ImportError:
    pass

# --- 1. RATE LIMITING (Task 1) ---
class ForceLoginRateThrottle(AnonRateThrottle):
    rate = '5/min'

# --- 2. REGISTRATION & SESSION (Task 1) ---
class RegisterUserView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

class SessionLoginView(views.APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ForceLoginRateThrottle] 
    
    @extend_schema(summary="Web Dashboard Login", request=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'], 
                password=serializer.validated_data['password']
            )
            if user is not None:
                login(request, user)
                return Response({"message": "Session Login Successful"})
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# --- 3. IDENTITY SERVICE (Task 2 & 3) ---

class RequestOTPView(views.APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        generate_otp(request.user.id)
        return Response({"message": "OTP sent (Check Console)."})

class VerifyOTPView(views.APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(request=OTPVerifySerializer)
    def post(self, request):
        code = request.data.get('otp_code')
        if verify_otp_logic(request.user.id, code):
            return Response({"message": "Phone number verified!"})
        return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

class VerifyNIDView(views.APIView):
    """Submits NID, Encrypts it, and Logs the action (Task 3)."""
    permission_classes = [IsAuthenticated]

    @extend_schema(request=NIDSubmitSerializer)
    def post(self, request):
        nid = request.data.get('nid_number')
        try:
            validate_nid(nid)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        user = request.user
        user.set_nid(nid) # Fernet Encryption
        user.is_verified = True
        user.save()

        AuditLog.objects.create(
            user=user,
            action="KYC_VERIFIED",
            ip_address=request.META.get('REMOTE_ADDR'),
            details=f"NID ending in {nid[-4:]} encrypted and saved."
        )
        return Response({"message": "Identity Verified and Encrypted!"})

# --- 4. PRIVACY RIGHTS (Task 3) ---

class ExportMyDataView(views.APIView):
    """Demonstrates Data Portability and Decryption."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Safe decryption for Demo
        try:
            decrypted_nid = user.get_nid() if user.encrypted_nid else "No NID on file"
        except Exception:
            decrypted_nid = "Decryption Error (Check ENCRYPTION_KEY)"

        AuditLog.objects.create(
            user=user,
            action="DATA_EXPORT",
            ip_address=request.META.get('REMOTE_ADDR'),
            details="User accessed private data export."
        )

        return Response({
            "username": user.username,
            "email": user.email,
            "is_verified": user.is_verified,
            "role": getattr(user, 'role', 'User'),
            "decrypted_nid_from_db": decrypted_nid
        })

class ForgetMeView(views.APIView):
    """Anonymizes user data (Right to be Forgotten)."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.email = "anonymized@ishemalink.com"
        user.encrypted_nid = None
        user.is_verified = False
        user.save()
        
        AuditLog.objects.create(
            user=user,
            action="RIGHT_TO_BE_FORGOTTEN",
            details="User requested data anonymization."
        )
        return Response({"message": "Your personal data has been anonymized."})

# --- 5. UTILITIES ---

class WhoAmIView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({
            "username": request.user.username,
            "is_verified": request.user.is_verified,
            "role": getattr(request.user, 'role', 'User'),
            "auth_method": "JWT" if request.auth else "Session"
        })

class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        logout(request)
        return Response({"message": "Logged out successfully."})
    

@extend_schema(tags=['Logistics Hierarchy'])
class ShipmentListView(generics.ListAPIView):
    serializer_class = ShipmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = request.user
        
        # 1. Gov Officials see everything
        if user.role == 'GOV':
            return Shipment.objects.all()
        
        # 2. Sector Agents only see shipments in their assigned sector
        if user.role == 'AGENT':
            return Shipment.objects.filter(sector=user.assigned_sector)
        
        # 3. Drivers only see shipments assigned to them
        if user.role == 'DRIVER':
            return Shipment.objects.filter(driver=user)
            
        # 4. Customers see their own shipments
        return Shipment.objects.filter(owner=user)
    
# View for Gov Role
@extend_schema(tags=['Logistics Hierarchy'])
class GovManifestListView(views.APIView):
    permission_classes = [IsAuthenticated, IsGovOfficial] # From your permissions.py

    def get(self, request):
        shipments = Shipment.objects.all()
        return Response({
            "report_type": "National Cargo Manifest",
            "inspector": request.user.username,
            "total_active_shipments": shipments.count(),
            "data": ShipmentSerializer(shipments, many=True, context={'request': request}).data
        })

# View for Role Management
@extend_schema(tags=['Logistics Hierarchy'])
class RoleListView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Returns the Roles defined in your User model
        return Response({
            "available_roles": [
                {"code": "CUSTOMER", "label": "Customer"},
                {"code": "DRIVER", "label": "Truck Driver"},
                {"code": "AGENT", "label": "Sector Agent"},
                {"code": "GOV", "label": "RURA Inspector"}
            ]
        })