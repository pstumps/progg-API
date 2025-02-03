from django.db import models
from .MatchPlayerModel import MatchPlayerModel
from .MatchesModel import MatchesModel

class MatchPlayerGraph(models.Model):
    match = models.ForeignKey(MatchesModel, on_delete=models.CASCADE)
    steam_id3 = models.BigIntegerField(null=False)
    timestamp = models.IntegerField()
    net_worth = models.IntegerField(null=True)
    player_damage = models.IntegerField(null=True)
    boss_damage = models.IntegerField(null=True)
    player_healing = models.IntegerField(null=True)
