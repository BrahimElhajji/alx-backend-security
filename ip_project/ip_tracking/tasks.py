from celery import shared_task
from django.utils.timezone import now, timedelta
from .models import RequestLog, SuspiciousIP

SENSITIVE_PATHS = ['/admin', '/login']

@shared_task
def detect_anomalies():
    one_hour_ago = now() - timedelta(hours=1)

    # Find IPs exceeding 100 requests in the past hour
    ip_request_counts = (
        RequestLog.objects
        .filter(timestamp__gte=one_hour_ago)
        .values('ip_address')
        .annotate(count=models.Count('id'))
        .filter(count__gt=100)
    )

    for entry in ip_request_counts:
        ip = entry['ip_address']
        reason = f"More than 100 requests in the last hour ({entry['count']} requests)"
        SuspiciousIP.objects.get_or_create(ip_address=ip, defaults={'reason': reason})

    # Find IPs accessing sensitive paths
    suspicious_access = (
        RequestLog.objects
        .filter(timestamp__gte=one_hour_ago, path__in=SENSITIVE_PATHS)
        .values('ip_address')
        .distinct()
    )

    for entry in suspicious_access:
        ip = entry['ip_address']
        reason = f"Accessed sensitive path in last hour"
        SuspiciousIP.objects.get_or_create(ip_address=ip, defaults={'reason': reason})
