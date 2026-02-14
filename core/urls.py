from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterUserView, 
    SessionLoginView, 
    LogoutView, 
    WhoAmIView,
    RequestOTPView,
    VerifyOTPView,
    VerifyNIDView  # Use the updated name here
)

urlpatterns = [
    # --- TASK 1: AUTHENTICATION ---
    path('auth/login/session/', SessionLoginView.as_view(), name='session-login'),
    path('auth/token/obtain/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', RegisterUserView.as_view(), name='register'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/whoami/', WhoAmIView.as_view(), name='whoami'),
    
    # --- TASK 2: IDENTITY ENDPOINTS ---
    path('identity/otp/request/', RequestOTPView.as_view(), name='request-otp'),
    path('identity/otp/verify/', VerifyOTPView.as_view(), name='verify-otp'),
    path('identity/kyc/nid/', VerifyNIDView.as_view(), name='kyc-nid'),
    
    # Legacy NID path (redirecting to the new Task 2 view)
    path('auth/verify-nid/', VerifyNIDView.as_view(), name='verify-nid'),
]