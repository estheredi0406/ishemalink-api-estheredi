from django.urls import path
from .views import CreateShipmentView, update_shipment_status, ShipmentListView # <--- New Import
from .pricing_views import PublicTariffView, ClearCacheView

urlpatterns = [
    # Task 3: Shipments
    path('shipments/', CreateShipmentView.as_view(), name='create-shipment'),
    path('shipments/<int:pk>/update/', update_shipment_status, name='update-status'),
    
    # Task 5: Paginated Manifests
    path('shipments/list/', ShipmentListView.as_view(), name='list-shipments'),

    # Task 4: Pricing
    path('pricing/tariffs/', PublicTariffView.as_view(), name='public-tariffs'),
    path('admin/cache/clear-tariffs/', ClearCacheView.as_view(), name='clear-cache'),
]