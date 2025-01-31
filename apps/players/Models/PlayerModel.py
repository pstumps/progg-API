from django.db import models
from proggbackend.services.DeadlockAPIAssets import deadlockAPIAssetsService
from proggbackend.services.SteamWebAPI import SteamWebAPIService
from .PlayerHeroModel import PlayerHeroModel
from ...heroes.Models.HeroesModel import HeroesModel
from ...matches.Models.MatchesModel import MatchesModel


class PlayerModel(models.Model):
    player_id = models.AutoField(primary_key=True)
    steam_id3 = models.BigIntegerField(null=True)
    name = models.CharField(max_length=100)
    icon = models.JSONField(null=True)
    region = models.CharField(max_length=2)
    private = models.BooleanField(default=False)
    rank = models.IntegerField(default=0)
    # This will need to be changed. A Player can have many matches, but a Match does not need to have many players, since it has MatchPlayers.
    matches = models.ManyToManyField(MatchesModel, related_name='playerModel')
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
    lastLogin = models.DateTimeField(null=True)
    timePlayed = models.IntegerField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    timelineTracking = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def getLastMatch(self):
        return self.matches.order_by('-date').first()

    def getTopPlayerHeroes(self):
        return self.player_hero_stats.order_by('tier')

    def calculatePlayerHeroTiers(self):
        playerHeroes = self.player_hero_stats.all()
        for hero in playerHeroes:
            score = self.calculateScore(hero)
            hero.tier = score
            hero.save()

    def calculateScore(self, hero):
        winrate = hero.wins / (hero.matches-hero.wins) * 100
        kda = (hero.kills + hero.assists) / hero.deaths

        winrate_weight = 0.6
        kda_weight = 0.45
        soulsPerMin_weight = 0.5
        heroDamage_weight = 0.1
        objDamage_weight = 0.1
        healing_weight = 0.075
        matches_weight = 0.35
        accuracy_weight = 0.15


        score = ((winrate * winrate_weight) +
                 (kda * kda_weight) +
                 (hero.soulsPerMin * soulsPerMin_weight) +
                 ((hero.heroDamage/hero.matches) * heroDamage_weight) +
                 (hero.matches * matches_weight) +
                 ((hero.objDamage/hero.matches) * objDamage_weight) +
                 ((hero.healing/hero.matches) * healing_weight) +
                 (accuracy_weight * (hero.accuracy*100)))

        return score

    def updatePlayerFromSteamWebAPI(self):
        steamWebAPI = SteamWebAPIService()
        playerData = steamWebAPI.getPlayerSummaries(steam_id3=self.steam_id3).get('response').get('players')
        if playerData[0]:
            self.name = playerData.get('personaname')
            self.icon = playerData.get('avatarfull')
            self.region = playerData.get('region')

        gameData = steamWebAPI.getOwnedGames(steam_id3=self.steam_id3).get('response')['games']
        if gameData:
            for games in gameData:
                if games['appid'] == 1422450:
                    self.timePlayed = games.get('playtime_forever') / 60

        self.save()

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
        self.longestStreak = max(self.longestStreak, stats['longestStreak'])
        self.accuracy = round(stats['accuracy'], 4) if stats['accuracy'] is not None else 1
        self.heroCritPercent = round(stats['heroCritPercent'], 4) if stats['heroCritPercent'] is not None else 1
        self.soulsPerMin = round(stats['soulsPerMin'], 4) if stats['soulsPerMin'] is not None else 1

        self.save()

    def updatePlayerStatsFromMatchPlayer(self, matchPlayer, multis, streaks, longestStreaks, objectiveEvents,
                                         midbossEvents):

        self.longestStreak = max(self.longestStreak, longestStreaks.get(matchPlayer.steam_id3, 0))

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
        if multis.get(matchPlayer.steam_id3):
            if any(multis[matchPlayer.steam_id3]):
                if not self.multis:
                    self.multis = multis.get(matchPlayer.steam_id3)
                else:
                    self.multis = [sum(x) for x in zip(self.multis, multis[matchPlayer.steam_id3])]
            else:
                self.multis = None

            if any(streaks[matchPlayer.steam_id3]):
                if not self.streaks:
                    self.streaks = streaks[matchPlayer.steam_id3]
                else:
                    self.streaks = [sum(x) for x in zip(self.streaks, streaks[matchPlayer.steam_id3])]
            else:
                self.streaks = None

        self.matches.add(matchPlayer.match)

        # Update player hero model
        hero = HeroesModel.objects.filter(hero_deadlock_id=matchPlayer.hero_deadlock_id).first()
        if not hero:
            DLAPIAssets = deadlockAPIAssetsService()
            heroName = DLAPIAssets.getHeroAssetsById(matchPlayer.hero_deadlock_id).get('name')
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
