from django.urls import path
from .views import (
    RegisterUserView, 
    SessionLoginView, 
    LogoutView, 
    WhoAmIView,
    RequestOTPView,
    VerifyOTPView,
    VerifyNIDView,
    ShipmentListView,
    ExportMyDataView, 
    ForgetMeView,
    GovManifestListView, # Added for Task 4
    RoleListView        # Added for Task 4
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

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

    # --- TASK 3: PRIVACY ---
    path('privacy/my-data/', ExportMyDataView.as_view(), name='export-data'),
    path('privacy/forget-me/', ForgetMeView.as_view(), name='forget-me'),

    # --- TASK 4: LOGISTICS & RBAC ---
    path('ops/shipments/', ShipmentListView.as_view(), name='shipment-list'),
    path('gov/manifests/', GovManifestListView.as_view(), name='gov-manifests'), # RURA View
    path('rbac/roles/', RoleListView.as_view(), name='role-list'),              # Role List
]