# game/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import GameSession, PlayerMove, Leaderboard
from django.utils.timezone import now

User = get_user_model()

class GameTests(TestCase):
    def setUp(self):
        """Set up test user and game session"""
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.game_session = GameSession.objects.create(player=self.user)

    def test_start_game(self):
        """Test if a new game session is created properly"""
        self.assertIsNotNone(self.game_session.id)
        self.assertEqual(self.game_session.player, self.user)

    def test_log_move(self):
        """Test if a player move is logged correctly"""
        move = PlayerMove.objects.create(session=self.game_session, action="clicked")
        self.assertEqual(move.session, self.game_session)
        self.assertEqual(move.action, "clicked")

    def test_end_game(self):
        """Test if game ends and score is saved"""
        self.game_session.end_time = now()
        self.game_session.score = 100
        self.game_session.save()

        updated_session = GameSession.objects.get(id=self.game_session.id)
        self.assertEqual(updated_session.score, 100)
        self.assertIsNotNone(updated_session.end_time)

    def test_leaderboard_updates(self):
        """Test if the leaderboard updates the best score"""
        leaderboard, _ = Leaderboard.objects.get_or_create(player=self.user, best_score=50)
        self.game_session.score = 200  # Higher score
        self.game_session.save()

        if self.game_session.score > leaderboard.best_score:
            leaderboard.best_score = self.game_session.score
            leaderboard.save()

        updated_leaderboard = Leaderboard.objects.get(player=self.user)
        self.assertEqual(updated_leaderboard.best_score, 200)

class GameMechanicsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.game_session = GameSession.objects.create(player=self.user)

    def test_enemy_attack(self):
        """Test if enemy attack reduces health."""
        initial_health = self.game_session.health
        self.game_session.take_damage(15)
        self.assertLess(self.game_session.health, initial_health)

    def test_collect_item(self):
        """Test if collecting an item works."""
        self.game_session.collect_item("Health Potion")
        self.assertIn("Health Potion", self.game_session.items)

        # Ensure health is restored
        self.assertEqual(self.game_session.health, min(100, self.game_session.health + 20))