from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterUserView, SessionLoginView, LogoutView

urlpatterns = [
    # Auth - Registration
    path('register/', RegisterUserView.as_view(), name='register'),

    # Task 1: Hybrid Authentication
    path('auth/login/session/', SessionLoginView.as_view(), name='login-session'), # Web
    path('auth/token/obtain/', TokenObtainPairView.as_view(), name='token_obtain'), # Mobile (JWT)
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
]