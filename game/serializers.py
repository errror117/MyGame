# game/serializers.py
from rest_framework import serializers
from .models import GameSession, PlayerMove, Leaderboard

class GameSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameSession
        fields = ['id', 'player', 'start_time', 'score']

class PlayerMoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerMove
        fields = ['id', 'session', 'timestamp', 'action']

class LeaderboardSerializer(serializers.ModelSerializer):
    player_name = serializers.CharField(source="player.username", read_only=True)  # Show player username

    class Meta:
        model = Leaderboard
        fields = ['player_name', 'best_score']
