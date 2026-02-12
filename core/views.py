from django.contrib.auth import authenticate, login, logout
from rest_framework import status, views, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiParameter

# Check if these imports exist in your project, if not, keep your old ones
from .serializers import UserRegistrationSerializer, NIDCheckSerializer
from .validators import validate_nid

# --- 1. The Security Guard (Rate Limiter) ---
class LoginRateThrottle(AnonRateThrottle):
    """
    Limits login attempts to 5 per minute (defined in settings.py).
    Blocks brute-force hackers.
    """
    scope = 'login_attempts' 

# --- 2. The Sign-Up Desk (Existing Logic) ---
class RegisterUserView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    Registers a new user (Agent or Customer).
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny] 

class NIDVerifyView(views.APIView):
    """
    POST /api/auth/verify-nid/
    Standalone check for NID validity.
    """
    permission_classes = [AllowAny]

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
                validate_nid(nid)
                return Response({"valid": True, "nid": nid}, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response({"valid": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- 3. The Web Login Door (New Logic) ---
class SessionLoginView(views.APIView):
    """
    POST /api/auth/login/session/
    Standard cookie-based login for Web Dashboard/Tablets.
    Includes Rate Limiting protection.
    """
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]  # <--- The Bouncer is watching

    @extend_schema(
        summary="Web Dashboard Login",
        description="Logs in via Session/Cookies. Recommended for shared tablets.",
        request=None, # You can add a serializer here for better docs later
        responses={200: "Login Successful", 401: "Invalid Credentials"}
    )
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        # Verify credentials
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Create the Session Cookie
            login(request, user)
            return Response({
                "message": "Session Login Successful",
                "role": user.role,
                "nid": user.nid
            })
        
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# --- 4. The Secure Exit (New Logic) ---
class LogoutView(views.APIView):
    """
    POST /api/auth/logout/
    Universal Logout: Invalidates Session AND Blacklists JWT Token.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Universal Logout",
        description="Invalidates Session AND Blacklists JWT Token."
    )
    def post(self, request):
        # A. Kill the Session (Web Users)
        logout(request)

        # B. Kill the Token (Mobile Users)
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist() # Adds token to 'Forbidden' list in DB
        except Exception:
            # If they didn't send a token, they were just a Session user.
            pass 

        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)

# --- 5. The Mirror (Debug Helper) ---
class WhoAmIView(views.APIView):
    """
    GET /api/auth/whoami/
    Returns current user details & auth method (Session vs Token).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "role": request.user.role,
            "nid": request.user.nid,
            "auth_method": "JWT" if request.auth else "Session"
        })