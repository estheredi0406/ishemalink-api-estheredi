from rest_framework import views, generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import AnonRateThrottle
from django.contrib.auth import authenticate, login, logout
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.tokens import RefreshToken

# --- Imports ---
try:
    from .serializers import UserRegistrationSerializer, NIDCheckSerializer, LoginSerializer
except ImportError:
    pass

# --- 1. THE NUCLEAR WEAPON (Force Rate Limit) ---
class ForceLoginRateThrottle(AnonRateThrottle):
    """
    This forces the limit to 5 per minute, ignoring settings.py.
    """
    rate = '5/min'

# --- 2. REGISTRATION (Legacy) ---
class RegisterUserView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

class NIDVerifyView(views.APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        return Response({"message": "NID Verification Endpoint"}, status=200)

# --- 3. SESSION LOGIN (Updated with Force Throttle) ---
class SessionLoginView(views.APIView):
    """
    POST /api/auth/login/session/
    Logs in via Session/Cookies. Protected by Hard-Coded Rate Limiting.
    """
    permission_classes = [AllowAny]
    
    # <--- THIS IS THE CHANGE: Use the class we defined above
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

# --- 4. LOGOUT ---
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

# --- 5. WHO AM I? ---
class WhoAmIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "role": getattr(request.user, 'role', 'Unknown'),
            "auth_method": "JWT" if request.auth else "Session"
        })