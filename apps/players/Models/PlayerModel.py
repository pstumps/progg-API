from django.db import models


class PlayerModel(models.Model):
    player_id = models.AutoField(primary_key=True)
    steam_id3 = models.BigIntegerField(null=True)
    name = models.CharField(max_length=100)
    player_tag = models.CharField(max_length=100)
    avatar = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    rank = models.IntegerField(default=0)
    matches = models.ManyToManyField('matches.MatchesModel', related_name='playersModel', symmetrical=True)
    wins = models.IntegerField(default=0)
    kills = models.IntegerField(default=0)
    deaths = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    souls = models.BigIntegerField(default=0)
    accuracy = models.IntegerField(default=0)
    heroDamage = models.BigIntegerField(default=0)
    objDamage = models.BigIntegerField(default=0)
    healing = models.BigIntegerField(default=0)
    guardians = models.IntegerField(default=0)
    walkers = models.IntegerField(default=0)
    baseGuardians = models.IntegerField(default=0)
    shieldGenerators = models.IntegerField(default=0)
    patrons = models.IntegerField(default=0)
    midbosses = models.IntegerField(default=0)
    lastHits = models.IntegerField(default=0)
    multis = models.JSONField(null=True) # [0, 0, 0, 0, 0, 0]
    streaks = models.JSONField(null=True) # [0, 0, 0, 0, 0, 0, 0]
    longestStreak = models.IntegerField(default=0)
    mmr = models.BigIntegerField(default=0)
    lastMatch = models.DateTimeField(null=True)
    lastLogin = models.DateTimeField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    timelineTracking = models.BooleanField(default=False)

    def __str__(self):
        return self.name
