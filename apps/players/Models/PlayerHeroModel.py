from django.db import models
from .PlayerModel import PlayerModel

class PlayerHeroModel(models.Model):
    player_hero_id = models.AutoField(primary_key=True)
    player = models.ForeignKey(PlayerModel, related_name='player_hero_stats', on_delete=models.CASCADE)
    hero = models.ForeignKey('heroes.HeroesModel', related_name='player_hero_stats', on_delete=models.CASCADE)
    wins = models.IntegerField(default=0)
    matches = models.IntegerField(default=0)
    kills = models.IntegerField(default=0)
    deaths = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    souls = models.BigIntegerField(default=0)
    accuracy = models.IntegerField(default=0)
    heroDamage = models.BigIntegerField(default=0)
    objDamage = models.BigIntegerField(default=0)
    healing = models.BigIntegerField(default=0)
    multis = models.JSONField(null=True) # [0, 0, 0, 0, 0, 0]
    streaks = models.JSONField(null=True) # [0, 0, 0, 0, 0, 0, 0]
    longestStreak = models.IntegerField(default=0)
    midBoss = models.IntegerField(default=0)
    tier = models.CharField(max_length=2, null=True)
    beta = models.BooleanField(default=0)

    def __str__(self):
        return self.hero.name
