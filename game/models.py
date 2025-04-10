# game/models.py

from django.db import models
from django.conf import settings
from django.utils.timezone import now
import json  # Needed for inventory storage

class GameSession(models.Model):
    """Tracks when a player starts & ends a game session."""
    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=now)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    health = models.IntegerField(default=100)  # New field: Health
    items = models.TextField(default="[]")  # JSON-encoded inventory list

    def __str__(self):
        return f"{self.player.username} - {self.score} points"

    def is_alive(self):
        """Check if player is still alive."""
        return self.health > 0

    def take_damage(self, damage):
        """Reduce player health."""
        self.health = max(0, self.health - damage)
        self.save()

    def collect_item(self, item):
        """Add item to inventory."""
        inventory = json.loads(self.items)  # Convert JSON string to list
        inventory.append(item)
        self.items = json.dumps(inventory)  # Convert back to JSON string
        self.save()

class PlayerMove(models.Model):
    """Logs actions taken by the player."""
    session = models.ForeignKey(GameSession, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=now)
    action = models.CharField(max_length=100)  # e.g., "clicked", "solved_puzzle"

class Leaderboard(models.Model):
    """Tracks top players & scores."""
    player = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    best_score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.player.username} - Best Score: {self.best_score}"
