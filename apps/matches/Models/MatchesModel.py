from django.db import models
from ...players.Models.PlayerModel import PlayerModel

class MatchesModel(models.Model):
    match_id = models.AutoField(primary_key=True)
    deadlock_id = models.BigIntegerField(null=True)
    date = models.DateTimeField(null=True)
    heroes = models.CharField(max_length=100, null=True)
    players = models.CharField(max_length=100, null=True)
    averageRank = models.IntegerField(null=True)
    gameMode = models.CharField(max_length=100, null=True)
    matchMode = models.CharField(max_length=100, null=True)
    length = models.IntegerField(null=True)


class MatchPlayerModel(models.Model):
    match_player_id = models.AutoField(primary_key=True)
    match_id = models.ForeignKey(MatchesModel, related_name='matchPlayerModel', on_delete=models.CASCADE)
    player_id = models.ForeignKey(PlayerModel, related_name='matchPlayerModel', on_delete=models.CASCADE)
    party = models.ManyToManyField('self', related_name='matchPlayerModel', symmetrical=True)
    kills = models.IntegerField(null=True)
    deaths = models.IntegerField(null=True)
    assists = models.IntegerField(null=True)
    hero = models.CharField(max_length=100, null=True)
    team = models.CharField(max_length=100, null=True)
    souls = models.BigIntegerField(null=True)
    level = models.IntegerField(null=True)
    heroDamage = models.IntegerField(null=True)
    objDamage = models.IntegerField(null=True)
    healing = models.IntegerField(null=True)
    lastHits = models.IntegerField(null=True)
    denies = models.IntegerField(null=True)
    win = models.BooleanField(null=True)
