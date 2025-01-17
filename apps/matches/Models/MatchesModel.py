from django.db import models
from ...players.Models.PlayerModel import PlayerModel


class MatchesModel(models.Model):
    match_id = models.AutoField(primary_key=True)
    deadlock_id = models.BigIntegerField(null=True)
    date = models.DateTimeField(null=True)
    averageRank = models.JSONField(null=True)
    gameMode = models.CharField(max_length=100, null=True)
    matchMode = models.CharField(max_length=100, null=True)
    length = models.IntegerField(default=0)
    teamStats = models.JSONField(null=True)
    victor = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.deadlock_id

    def calculateTeamStats(self):
        team_aggregate_stats = self.matchPlayerModels.values('team').annotate(
            kills=models.Sum('kills'),
            deaths=models.Sum('deaths'),
            assists=models.Sum('assists'),
            heroDamage=models.Sum('heroDamage'),
            objDamage=models.Sum('objDamage'),
            healing=models.Sum('healing'),
            souls=models.Sum('souls'),
            avgHeroDamage=models.Avg('heroDamage'),
            avgObjDamage=models.Avg('objDamage'),
            avgHealing=models.Avg('healing'),
            avgSouls=models.Avg('souls'),
            avgLastHits=models.Avg('lastHits'),
            avgDenies=models.Avg('denies'),
        )

        teamStatsDict = {stat['team']: stat for stat in team_aggregate_stats}
        self.teamStats = {'teamStats': teamStatsDict}
        self.save()


