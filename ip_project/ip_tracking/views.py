from django.shortcuts import render
from ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='10/m', method='POST', block=True)
@ratelimit(key='ip', rate='5/m', method='GET', block=True)
def sensitive_view(request):
    return JsonResponse({'message': 'You have accessed a rate-limited view.'})
# Create your views here.
