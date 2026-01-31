from django.urls import path
from .views import CreateCargoView

urlpatterns = [
    path('cargo/', CreateCargoView.as_view(), name='cargo-list'),
]