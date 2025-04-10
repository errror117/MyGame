# authentication/views.py

from django.views.decorators.csrf import csrf_exempt 
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, get_user_model
from django.utils.timezone import now
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
import logging

logger = logging.getLogger(__name__)

# Get the correct User model dynamically
User = get_user_model()

# ------------------------------
# 🔹 PERMISSIONS
# ------------------------------
class IsSuperUser(BasePermission):
    """Custom permission to allow only superusers to access an endpoint."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

# ------------------------------
# 🔹 AUTHENTICATION & USER MANAGEMENT
# ------------------------------
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
    """API endpoint to create a new user with roles."""
    username = request.data.get('username')
    password = request.data.get('password')
    role = request.data.get('role', 'player')  # Default role is 'player'

    if not username or not password:
        return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    if role not in ['player', 'admin']:
        return Response({'error': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password)
    if hasattr(user, 'role'):  # Ensure role exists in CustomUser model
        user.role = role  
        user.save()

    return Response({'message': 'User created successfully', 'role': role}, status=status.HTTP_201_CREATED)

@csrf_exempt
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

# ------------------------------
# 🔹 PROTECTED ADMIN DASHBOARD
# ------------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard(request):
    """An admin-only API endpoint."""
    if not hasattr(request.user, 'role') or request.user.role != 'admin':
        return Response({'error': 'You do not have permission to access this resource'}, status=status.HTTP_403_FORBIDDEN)

    return Response({'message': 'Welcome, Admin! Here’s your dashboard.'}, status=status.HTTP_200_OK)

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

# ------------------------------
# 🔹 GAME SESSION MANAGEMENT
# ------------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def start_game(request):
    """Start a new survival session and track survival time."""
    
    # Ensure the session is created
    if not request.session.session_key:
        request.session.create()

    request.session["start_time"] = now().isoformat()  # Store session start time
    request.session["health"] = 100  # Player starts with full health
    request.session.modified = True  # Ensure session changes are saved

    return Response({
        "message": "Game session started!",
        "session_id": request.session.session_key,
        "health": request.session["health"],
        "start_time": request.session["start_time"],
    }, status=status.HTTP_201_CREATED)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_survival_time(request):
    """Check how long the player has survived."""
    
    # Ensure there is an active session
    if "start_time" not in request.session:
        return Response({"error": "No active game session."}, status=status.HTTP_400_BAD_REQUEST)

    start_time = now().fromisoformat(request.session["start_time"])
    survival_time = (now() - start_time).total_seconds()  # Get survival time in seconds

    return Response({
        "message": "Survival time fetched successfully!",
        "survival_time": survival_time,
        "health": request.session.get("health", 100)  # Ensure health is retrieved correctly
    })

