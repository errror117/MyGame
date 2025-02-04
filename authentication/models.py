from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):  # Extending Django's built-in User model
    score = models.IntegerField(default=0)  # Extra field for game score

    def __str__(self):
        return self.username
