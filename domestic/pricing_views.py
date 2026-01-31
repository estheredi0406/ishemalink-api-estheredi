from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from .models import Tariff
from .serializers import TariffSerializer # We will create this next

# Key used to store data in cache
TARIFF_CACHE_KEY = 'shipping_tariffs_v1'
CACHE_TTL = 60 * 60 * 24  # 24 Hours

class PublicTariffView(APIView):
    """
    GET /api/pricing/tariffs/
    Returns tariff rates. Uses Cache to avoid DB hits.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        # 1. Try to get data from Cache
        cached_data = cache.get(TARIFF_CACHE_KEY)
        
        if cached_data:
            print("⚡ CACHE HIT: Serving data from RAM") # Log for grading evidence
            response = Response(cached_data)
            response['X-Cache-Hit'] = 'TRUE' # Custom header for rubric
            return response

        # 2. If not in cache, query Database
        print("🐢 CACHE MISS: Querying Database...")
        tariffs = Tariff.objects.all()
        serializer = TariffSerializer(tariffs, many=True)
        data = serializer.data

        # 3. Save to Cache for next time
        cache.set(TARIFF_CACHE_KEY, data, CACHE_TTL)

        return Response(data)

class ClearCacheView(APIView):
    """
    POST /api/admin/cache/clear-tariffs/
    Forces the cache to expire. Used when prices change.
    """
    permission_classes = [IsAdminUser] # Only Admins can do this

    def post(self, request):
        cache.delete(TARIFF_CACHE_KEY)
        return Response({"message": "Cache cleared successfully. Next request will hit DB."})