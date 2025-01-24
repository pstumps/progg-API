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
    soulsPerMin = models.FloatField(default=0)
    accuracy = models.FloatField(default=0)
    heroCritPercent = models.FloatField(default=0)
    heroDamage = models.BigIntegerField(default=0)
    objDamage = models.BigIntegerField(default=0)
    healing = models.BigIntegerField(default=0)
    guardians = models.IntegerField(default=0)
    walkers = models.IntegerField(default=0)
    baseGuardians = models.IntegerField(default=0)
    shieldGenerators = models.IntegerField(default=0)
    patrons = models.IntegerField(default=0)
    midbosses = models.IntegerField(default=0)
    rejuvinators = models.IntegerField(default=0)
    laneCreeps = models.IntegerField(default=0)
    neutralCreeps = models.IntegerField(default=0)
    lastHits = models.IntegerField(default=0)
    denies = models.IntegerField(default=0)
    multis = models.JSONField(null=True) # [0, 0, 0, 0, 0, 0]
    streaks = models.JSONField(null=True) # [0, 0, 0, 0, 0, 0, 0]
    longestStreak = models.IntegerField(default=0)
    mmr = models.BigIntegerField(default=0)
    lastMatch = models.DateTimeField(null=True)
    lastLogin = models.DateTimeField(null=True)
    timePlayed = models.IntegerField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    timelineTracking = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def updatePlayerStats(self):
        accuracyArray = []
        critArray = []
        soulsPerMinArray = []
        for playerHeros in self.player_hero_stats.all():
            self.wins += playerHeros.wins
            self.kills += playerHeros.kills
            self.deaths += playerHeros.deaths
            self.assists += playerHeros.assists
            self.souls += playerHeros.souls
            accuracyArray.append(playerHeros.accuracy)
            critArray.append(playerHeros.heroCritPercent)
            self.heroDamage += playerHeros.heroDamage
            self.objDamage += playerHeros.objDamage
            self.healing += playerHeros.healing
            self.laneCreeps += playerHeros.laneCreeps
            self.neutralCreeps += playerHeros.neutralCreeps
            self.midbosses += playerHeros.midBoss
            self.lastHits += playerHeros.lastHits
            self.denies += playerHeros.denies
            if playerHeros.longestStreak > self.longestStreak:
                self.longestStreak = playerHeros.longestStreak

        self.soulsPerMin = sum(soulsPerMinArray) / len(soulsPerMinArray) if len(soulsPerMinArray) > 0 else 1
        self.accuracy = sum(accuracyArray) / len(accuracyArray) if len(soulsPerMinArray) > 0 else 1
        self.heroCritPercent = sum(critArray) / len(critArray) if len(soulsPerMinArray) > 0 else 1

        self.save()
