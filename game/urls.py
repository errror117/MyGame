# game/urls.py

from django.urls import path
from .views import (
    start_game, log_move, end_game, 
    get_survival_time, enemy_attack, 
    collect_item, game_home, leaderboard_view,
    login_view, register_view
)

app_name = "game"

urlpatterns = [
    path("start/", start_game, name="start-game"),
    path("move/", log_move, name="log-move"),
    path("end/", end_game, name="end-game"),
    path("survival-time/", get_survival_time, name="survival-time"),
    path("enemy-attack/", enemy_attack, name="enemy-attack"),
    path("collect-item/", collect_item, name="collect-item"),
    
    # Frontend Pages
    path("", game_home, name="game-home"),  # Home Page
    path("leaderboard/", leaderboard_view, name="leaderboard"),
    
    # Authentication
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
]
