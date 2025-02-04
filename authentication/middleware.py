from django.http import JsonResponse
from rest_framework.exceptions import APIException

class CustomExceptionMiddleware:
    """Middleware to handle all exceptions globally and return JSON responses."""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except APIException as e:
            return JsonResponse({'error': str(e.detail)}, status=e.status_code)
        except Exception as e:
            return JsonResponse({'error': 'Internal Server Error'}, status=500)
