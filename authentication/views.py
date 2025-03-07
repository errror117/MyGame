from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission
import logging


logger = logging.getLogger(__name__)


class IsSuperUser(BasePermission):
    """Custom permission to allow only superusers to access an endpoint."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

class ProtectedView(APIView):
     """A sample API that requires authentication."""
     permission_classes = [IsAuthenticated]

     def get(self, request):
        logger.debug(f"Request Headers: {request.headers}")
        logger.debug(f"Authenticated User: {request.user}")

        if request.user.is_authenticated:
            return Response({'message': f'Hello, {request.user.username}! JWT is working.'}, status=200)
        else:
            logger.debug("User is not authenticated!")
            return Response({'detail': 'User is not authenticated'}, status=403)
    
def get_tokens_for_user(user):
    """Generate JWT tokens for a user."""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@csrf_exempt
@api_view(['POST'])
def register(request):
    """API endpoint to create a new user."""
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password)
    return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Disable CSRF for login API
@api_view(['POST'])
def login(request):
    """API endpoint for user login."""
    print("\nReceived Request Data:", request.data)  # Debugging
    
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Both username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if user is not None:
        tokens = get_tokens_for_user(user)  # Generate JWT tokens
        return Response({'message': 'Login successful', 'tokens': tokens}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
