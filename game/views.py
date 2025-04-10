# game/views.py

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from rest_framework import status
from django.utils.timezone import now
import random
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import GameSession, PlayerMove, Leaderboard
from .serializers import GameSessionSerializer, PlayerMoveSerializer, LeaderboardSerializer

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@csrf_exempt
def start_game(request):
    """Starts a new game session and returns the session ID."""
    session = GameSession.objects.create(player=request.user)
    return JsonResponse({"message": "Game started!", "session_id": session.id})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def log_move(request):
    """Log a player's move during the game."""
    session_id = request.data.get("session_id")
    action = request.data.get("action")

    try:
        session = GameSession.objects.get(id=session_id, player=request.user)
        move = PlayerMove.objects.create(session=session, action=action)
        return Response({"message": "Move logged!", "move_id": move.id}, status=status.HTTP_201_CREATED)
    except GameSession.DoesNotExist:
        return Response({"error": "Invalid session!"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def end_game(request):
    """End the game session and update the leaderboard."""
    session_id = request.data.get("session_id")
    score = request.data.get("score", 0)

    try:
        session = GameSession.objects.get(id=session_id, player=request.user)
        session.end_time = now()
        session.score = score
        session.save()

        # Update the leaderboard
        leaderboard, _ = Leaderboard.objects.get_or_create(player=request.user)
        if score > leaderboard.best_score:
            leaderboard.best_score = score
            leaderboard.save()

        return Response({"message": "Game ended!", "final_score": score}, status=status.HTTP_200_OK)
    except GameSession.DoesNotExist:
        return Response({"error": "Invalid session!"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def enemy_attack(request):
    """Enemy attack reduces player's health randomly."""
    session_id = request.data.get("session_id")

    try:
        session = GameSession.objects.get(id=session_id, player=request.user)

        if not session.is_alive():
            return Response({"error": "Game Over!"}, status=status.HTTP_400_BAD_REQUEST)

        damage = random.randint(5, 20)  # Random damage
        session.take_damage(damage)

        return Response({
            "message": f"Enemy attacked! You lost {damage} HP.",
            "remaining_health": session.health
        }, status=status.HTTP_200_OK)

    except GameSession.DoesNotExist:
        return Response({"error": "Invalid session!"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def collect_item(request):
    """Collect an item and gain a bonus."""
    session_id = request.data.get("session_id")
    item = request.data.get("item")  # Example: "Health Potion"

    try:
        session = GameSession.objects.get(id=session_id, player=request.user)

        if not session.is_alive():
            return Response({"error": "Game Over!"}, status=status.HTTP_400_BAD_REQUEST)

        session.collect_item(item)

        # If it's a health potion, restore health
        if item == "Health Potion":
            session.health = min(100, session.health + 20)
            session.save()

        return Response({
            "message": f"You collected a {item}!",
            "inventory": session.items,
            "health": session.health
        }, status=status.HTTP_200_OK)

    except GameSession.DoesNotExist:
        return Response({"error": "Invalid session!"}, status=status.HTTP_400_BAD_REQUEST)

def get_survival_time(request):
    """Returns survival time message."""
    return JsonResponse({"message": "Survival time will be implemented soon!"}, status=200)

@login_required
def game_home(request):
    """Render the game home page."""
    return render(request, "game/index.html")

@login_required
def leaderboard_view(request):
    """Render the leaderboard page with top players."""
    top_players = Leaderboard.objects.order_by("-best_score")[:10]
    return render(request, "game/leaderboard.html", {"leaderboard": top_players})

def login_view(request):
    """Handles user login."""
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("game:game-home")  # Redirect to home page after login
    else:
        form = AuthenticationForm()
    print("login_view triggered")
    return render(request, "game/login.html", {"form": form})

def register_view(request):
    """Handles user registration."""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("game:game-home")  # Redirect to home page after registration
    else:
        form = UserCreationForm()
    return render(request, "game/register.html", {"form": form})
