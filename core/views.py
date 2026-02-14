from rest_framework import views, generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import AnonRateThrottle
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.tokens import RefreshToken

# Internal Imports
from .utils import generate_otp, verify_otp_logic
from .validators import validate_nid

# --- Imports: Serializers ---
try:
    from .serializers import (
        UserRegistrationSerializer, 
        NIDCheckSerializer, 
        LoginSerializer,
        OTPVerifySerializer, # New for Task 2
        NIDSubmitSerializer  # New for Task 2
    )
except ImportError:
    pass

# --- 1. THE NUCLEAR WEAPON (Force Rate Limit) ---
class ForceLoginRateThrottle(AnonRateThrottle):
    rate = '5/min'

# --- 2. REGISTRATION & SESSION (Task 1) ---
class RegisterUserView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

class SessionLoginView(views.APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ForceLoginRateThrottle] 
    
    @extend_schema(
        summary="Web Dashboard Login",
        request=LoginSerializer, 
        responses={200: "Login Successful", 401: "Invalid Credentials"}
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(request, 
                              username=serializer.validated_data['username'], 
                              password=serializer.validated_data['password'])

            if user is not None:
                login(request, user)
                return Response({"message": "Session Login Successful"})
        
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# --- 3. IDENTITY SERVICE (Task 2: OTP & NID) ---

class RequestOTPView(views.APIView):
    """Generates a 6-digit code for +250 numbers."""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Request SMS OTP")
    def post(self, request):
        generate_otp(request.user.id)
        return Response({"message": "OTP sent to your registered phone (Check Console)."})

class VerifyOTPView(views.APIView):
    """Verifies the code from the mock SMS service."""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(request=OTPVerifySerializer)
    def post(self, request):
        code = request.data.get('otp_code')
        if verify_otp_logic(request.user.id, code):
            return Response({"message": "Phone number verified successfully!"})
        return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

class VerifyNIDView(views.APIView):
    """Submits NID and unlocks the account status to verified."""
    permission_classes = [IsAuthenticated]

    @extend_schema(request=NIDSubmitSerializer)
    def post(self, request):
        nid = request.data.get('nid_number')
        
        try:
            validate_nid(nid)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        user = request.user
        user.nid = nid
        user.is_verified = True # Sets account to verified
        user.save()
        
        return Response({"message": "Identity Verified! Account unlocked."})

# --- 4. UTILITIES ---

class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                RefreshToken(refresh_token).blacklist()
        except Exception:
            pass
        return Response({"message": "Logged out successfully."}, status=200)

class WhoAmIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "is_verified": request.user.is_verified, # Added for Task 2 proof
            "role": getattr(request.user, 'role', 'Unknown'),
            "auth_method": "JWT" if request.auth else "Session"
        })