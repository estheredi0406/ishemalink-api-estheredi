from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterUserView, NIDVerifyView, SessionLoginView, LogoutView, WhoAmIView

urlpatterns = [
   
    path('auth/login/session/', SessionLoginView.as_view(), name='session-login'),
# JWT AUTH (Mobile App) 
    path('auth/token/obtain/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', RegisterUserView.as_view(), name='register'),
    path('auth/verify-nid/', NIDVerifyView.as_view(), name='verify-nid'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/whoami/', WhoAmIView.as_view(), name='whoami'),
]