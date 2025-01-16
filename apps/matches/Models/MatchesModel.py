from django.db import models
from ...players.Models.PlayerModel import PlayerModel


def getAverageDenies(matchId, teamName):
    avgDenies = MatchPlayerModel.objects.filter(
        match__match_id=matchId,
        team=teamName
    ).aggregate(models.Avg('denies'))['denies__avg']
    return avgDenies


def getAverageLastHits(matchId, teamName):
    avgLastHits = MatchPlayerModel.objects.filter(
        match__match_id=matchId,
        team=teamName
    ).aggregate(models.Avg('lastHits'))['lastHits__avg']
    return avgLastHits


def getAverageHealing(matchId, teamName):
    avgHealing = MatchPlayerModel.objects.filter(
        match__match_id=matchId,
        team=teamName
    ).aggregate(models.Avg('healing'))['healing__avg']
    return avgHealing


def getAverageObjDamage(matchId, teamName):
    avgObjDmg = MatchPlayerModel.objects.filter(
        match__match_id=matchId,
        team=teamName
    ).aggregate(models.Avg('objDamage'))['objDamage__avg']
    return avgObjDmg


def getAverageHeroDamage(matchId, teamName):
    avgHeroDmg = MatchPlayerModel.objects.filter(
        match__match_id=matchId,
        team=teamName
    ).aggregate(models.Avg('heroDamage'))['heroDamage__avg']
    return avgHeroDmg


def getAverageNetWorth(matchId, teamName):
    avgNetWorth = MatchPlayerModel.objects.filter(
        match__match_id=matchId,
        team=teamName
    ).aggregate(models.Avg('souls'))['souls__avg']
    return avgNetWorth


class MatchesModel(models.Model):
    match_id = models.AutoField(primary_key=True)
    deadlock_id = models.BigIntegerField(null=True)
    date = models.DateTimeField(null=True)
    averageRank = models.IntegerField(default=0)
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


class MatchPlayerModel(models.Model):
    match_player_id = models.AutoField(primary_key=True)
    steam_id3 = models.BigIntegerField()
    match = models.ForeignKey(MatchesModel, related_name='matchPlayerModels', on_delete=models.CASCADE)
    player = models.ForeignKey(PlayerModel, related_name='matchPlayerModels', on_delete=models.CASCADE, null=True)
    party = models.ManyToManyField('self', related_name='matchPlayerModels', symmetrical=True, null=True)
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
