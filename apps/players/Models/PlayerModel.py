import json
from django.db import models
from proggbackend.services import deadlockAPIAssetsService
from .PlayerHeroModel import PlayerHeroModel
from ...heroes.Models.HeroesModel import HeroesModel
from ...matches.Models.MatchesModel import MatchesModel


class PlayerModel(models.Model):
    player_id = models.AutoField(primary_key=True)
    steam_id3 = models.BigIntegerField(null=True)
    name = models.CharField(max_length=100)
    player_tag = models.CharField(max_length=100)
    avatar = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    rank = models.IntegerField(default=0)
    matches = models.ManyToManyField(MatchesModel, related_name='playersModel')
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
        stats = self.player_hero_stats.aggregate(
            wins=models.Sum('wins'),
            kills=models.Sum('kills'),
            deaths=models.Sum('deaths'),
            assists=models.Sum('assists'),
            souls=models.Sum('souls'),
            heroDamage=models.Sum('heroDamage'),
            objDamage=models.Sum('objDamage'),
            healing=models.Sum('healing'),
            laneCreeps=models.Sum('laneCreeps'),
            neutralCreeps=models.Sum('neutralCreeps'),
            midbosses=models.Sum('midBoss'),
            lastHits=models.Sum('lastHits'),
            denies=models.Sum('denies'),
            longestStreak=models.Max('longestStreak'),
            accuracy=models.Avg('accuracy'),
            heroCritPercent=models.Avg('heroCritPercent'),
            soulsPerMin=models.Avg('soulsPerMin')
        )

        self.wins = stats['wins'] or 0
        self.kills = stats['kills'] or 0
        self.deaths = stats['deaths'] or 0
        self.assists = stats['assists'] or 0
        self.souls = stats['souls'] or 0
        self.heroDamage = stats['heroDamage'] or 0
        self.objDamage = stats['objDamage'] or 0
        self.healing = stats['healing'] or 0
        self.laneCreeps = stats['laneCreeps'] or 0
        self.neutralCreeps = stats['neutralCreeps'] or 0
        self.midbosses = stats['midbosses'] or 0
        self.lastHits = stats['lastHits'] or 0
        self.denies = stats['denies'] or 0
        self.longestStreak = max( self.longestStreak, stats['longestStreak'])
        self.accuracy = round(stats['accuracy'], 4) if stats['accuracy'] is not None else 1
        self.heroCritPercent = round(stats['heroCritPercent'], 4) if stats['heroCritPercent'] is not None else 1
        self.soulsPerMin = round(stats['soulsPerMin'], 4) if stats['soulsPerMin'] is not None else 1

        self.save()

    def updatePlayerStatsFromMatchPlayer(self, matchPlayer, multis, streaks, longestStreaks, objectiveEvents,
                                         midbossEvents):
        self.longestStreak = max(self.longestStreak, longestStreaks[matchPlayer.steam_id3])

        for event in midbossEvents:
            if event.team == matchPlayer.team:
                self.rejuvinators += 1
            if event.slayer == matchPlayer.team:
                self.midbosses += 1

        for event in objectiveEvents:
            if event.team == matchPlayer.team:
                if 'Tier1' in event.target:
                    self.guardians += 1
                elif 'Tier2' in event.target:
                    self.walkers += 1
                elif 'BarrackBoss' in event.target:
                    self.baseGuardians += 2
                elif 'TitanShieldGenerator' in event.target:
                    self.shieldGenerators += 1
                elif 'k_eCitadelTeamObjective_Core' in event.target:
                    self.patrons += 1

        if any(multis[matchPlayer.steam_id3]):
            if not self.multis:
                self.multis = json.dumps({'multis': multis[matchPlayer.steam_id3]})
            else:
                self.multis = json.dumps({'multis': [sum(x) for x in zip(json.loads(self.multis)['multis'],
                                                                           multis[matchPlayer.steam_id3])]})
        else:
            self.multis = None

        if any(streaks[matchPlayer.steam_id3]):
            if not self.streaks:
                self.streaks = json.dumps({'streaks': streaks[matchPlayer.steam_id3]})
            else:
                self.streaks = json.dumps({'streaks': [sum(x) for x in zip(json.loads(self.streaks)['streaks'],
                                                                             streaks[matchPlayer.steam_id3])]})
        else:
            self.streaks = None

        self.matches.add(matchPlayer.match)


        # Update player hero model
        hero = HeroesModel.objects.filter(hero_deadlock_id=matchPlayer.hero_deadlock_id).first()
        if not hero:
            DLAPIAssets = deadlockAPIAssetsService()
            heroName = DLAPIAssets.getHeroAssetsById(matchPlayer.hero_deadlock_id)['name']
            hero = HeroesModel.objects.create(
                name=heroName,
                hero_deadlock_id=matchPlayer.hero_deadlock_id
            )
        playerHero = PlayerHeroModel.objects.filter(player=matchPlayer.player, hero=hero).first()
        if not playerHero:
            playerHero = PlayerHeroModel.objects.create(
                player=matchPlayer.player,
                hero=hero
            )

        playerHero.createOrUpdatePlayerHero(matchPlayer, longestStreaks)


        self.save()
