from django.db import models


class PlayerHeroModel(models.Model):
    player_hero_id = models.AutoField(primary_key=True)
    player = models.ForeignKey('players.PlayerModel', related_name='player_hero_stats', on_delete=models.CASCADE)
    hero = models.ForeignKey('heroes.HeroesModel', related_name='player_hero_stats', on_delete=models.CASCADE)
    wins = models.IntegerField(default=0)
    matches = models.IntegerField(default=0)
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
    laneCreeps = models.IntegerField(default=0)
    neutralCreeps = models.IntegerField(default=0)
    lastHits = models.IntegerField(default=0)
    denies = models.IntegerField(default=0)
    multis = models.JSONField(null=True) # [0, 0, 0, 0, 0, 0] Not tracking these atm
    streaks = models.JSONField(null=True) # [0, 0, 0, 0, 0, 0, 0] Not tracking these atm
    longestStreak = models.IntegerField(default=0)
    midBoss = models.IntegerField(default=0) # Not tracking atm
    tier = models.CharField(max_length=2, null=True)
    beta = models.BooleanField(default=0)

    def __str__(self):
        return self.hero.name

    def createOrUpdatePlayerHero(self, matchPlayer, longestStreaks):
        self.wins += 1 if matchPlayer.win else 0
        self.matches += 1
        self.kills += matchPlayer.kills
        self.deaths += matchPlayer.deaths
        self.assists += matchPlayer.assists
        self.souls += matchPlayer.souls
        self.soulsPerMin = (self.soulsPerMin + matchPlayer.soulsPerMin) / 2
        self.heroDamage += matchPlayer.heroDamage
        self.objDamage += matchPlayer.objDamage
        self.healing += matchPlayer.healing
        self.laneCreeps += matchPlayer.laneCreeps
        self.neutralCreeps += matchPlayer.neutralCreeps
        self.lastHits += matchPlayer.lastHits
        self.denies += matchPlayer.denies
        self.longestStreak = max(self.longestStreak, longestStreaks.get(matchPlayer.steam_id3)) if longestStreaks.get(matchPlayer.steam_id3) else self.longestStreak
        if self.accuracy == 0:
            self.accuracy = matchPlayer.accuracy
        else:
            self.accuracy = (self.accuracy + matchPlayer.accuracy) / 2
        if self.heroCritPercent == 0:
            self.heroCritPercent = matchPlayer.heroCritPercent
        else:
            self.heroCritPercent = (self.heroCritPercent + matchPlayer.heroCritPercent) / 2

        self.save()
