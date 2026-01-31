from django.urls import path
from .views import RegisterUserView, NIDVerifyView

urlpatterns = [
    path('auth/register/', RegisterUserView.as_view(), name='register'),
    path('auth/verify-nid/', NIDVerifyView.as_view(), name='verify-nid'),
]