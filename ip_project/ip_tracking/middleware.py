import logging
from ipware import get_client_ip
from .models import RequestLog, BlockeIP
from django.core.cache import cache
from ipgeolocation import IpGeolocationAPI
from django.http import HttpResponseForbidden

logger = logging.getLogger(__name__)

class IPLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip, _ = get_client_ip(request)
        path = request.path

        if ip is None:
            ip = '0.0.0.0'

        # Check if IP is blocked
        if BlockedIP.objects.filter(ip_address=ip).exists():
            logger.warning(f"Blocked IP {ip} tried to access {path}")
            return HttpResponseForbidden("Your IP has been blocked.")

        # Check geolocation cache
        geo_data = cache.get(ip)
        if not geo_data:
            response = self.geo.get_geolocation(ip_address=ip)
            geo_data = {
                'country': response.get('country_name', ''),
                'city': response.get('city', '')
            }
            cache.set(ip, geo_data, timeout=60 * 60 * 24)  # Cache for 24 hours

        # Save to database
        RequestLog.objects.create(
            ip_address=ip,
            path=path,
            country=geo_data['country'],
            city=geo_data['city']
        )

        logger.info(f"Request from {ip} ({geo_data['country']}, {geo_data['city']}) to {path}")
        return self.get_response(request)
