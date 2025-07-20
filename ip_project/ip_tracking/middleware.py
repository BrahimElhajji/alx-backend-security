import logging
from ipware import get_client_ip
from .models import RequestLog

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

        # Log the request
        RequestLog.objects.create(ip_address=ip, path=path)
        logger.info(f"Request from {ip} to {path}")

        return self.get_response(request)
