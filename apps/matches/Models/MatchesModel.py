from django.db import models


class MatchesModel(models.Model):
    match_id = models.AutoField(primary_key=True)
    deadlock_id = models.BigIntegerField(null=True, db_index=True, unique=True)
    date = models.BigIntegerField(null=True)
    averageRank = models.JSONField(null=True)
    gameMode = models.CharField(max_length=50, null=True)
    matchMode = models.CharField(max_length=50, null=True)
    length = models.IntegerField(default=0)
    teamStats = models.JSONField(null=True)
    victor = models.CharField(max_length=50, null=True)

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
        )

        # Get rid of the 'team' key in the dictionary
        teamStatsDict = {stat['team']: {k: v for k, v in stat.items() if k != 'team'} for stat in team_aggregate_stats}

        self.teamStats = teamStatsDict
        self.save()


