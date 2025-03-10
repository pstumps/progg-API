from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.players.models import PlayerModel
from apps.matches.models import MatchesModel

class User(AbstractUser):
    firstName = models.CharField(max_length=100, blank=True)
    lastName = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    favorites = models.ManyToManyField(
        PlayerModel,
        blank=True,
        related_name='player_favorites'
    )
    match_favorites = models.ManyToManyField(
        MatchesModel,
        blank=True,
        related_name='match_favorites'
    )


    def __str__(self):
        return self.username