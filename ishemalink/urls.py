from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Task 2 Endpoints
    path('api/', include('core.urls')),

    # Task 3: Domestic Logistics
    path('api/domestic/', include('domestic.urls')), # <--- ADDED THIS

    path('api/international/', include('international.urls')),

    # Task 1: Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]