from django.db import models
from ...players.Models.PlayerModel import PlayerModel

class MatchesModel(models.Model):
    match_id = models.AutoField(primary_key=True)
    deadlock_id = models.BigIntegerField(null=True)
    date = models.DateTimeField(null=True)
    averageRank = models.IntegerField(default=0)
    gameMode = models.CharField(max_length=100, null=True)
    matchMode = models.CharField(max_length=100, null=True)
    length = models.IntegerField(default=0)


class MatchPlayerModel(models.Model):
    match_player_id = models.AutoField(primary_key=True)
    match = models.ForeignKey(MatchesModel, related_name='matchPlayerModel', on_delete=models.CASCADE)
    player = models.ForeignKey(PlayerModel, related_name='matchPlayerModel', on_delete=models.CASCADE)
    party = models.ManyToManyField('self', related_name='matchPlayerModel', symmetrical=True, null=True)
    kills = models.IntegerField(default=0)
    deaths = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    hero = models.CharField(max_length=100, null=True)
    team = models.CharField(max_length=100, null=True)
    souls = models.BigIntegerField(default=0)
    level = models.IntegerField(default=0)
    accuracy = models.FloatField(default=0)
    heroDamage = models.IntegerField(default=0)
    objDamage = models.IntegerField(default=0)
    healing = models.IntegerField(default=0)
    lastHits = models.IntegerField(default=0)
    denies = models.IntegerField(default=0)
    win = models.BooleanField(default=0)
    medals = models.JSONField(null=True)
    abandoned = models.BooleanField(default=False)
    abandonedTime = models.BigIntegerField(default=0)
