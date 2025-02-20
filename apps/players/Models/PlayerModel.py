import time
from django.db import models
from proggbackend.services.DeadlockAPIAssets import deadlockAPIAssetsService
from proggbackend.services.SteamWebAPI import SteamWebAPIService
from .PlayerHeroModel import PlayerHeroModel
from .PlayerRecords import PlayerRecords
from ...heroes.Models.HeroesModel import HeroesModel
from ...matches.Models.MatchesModel import MatchesModel

def current_timestamp():
    return int(time.time())


class PlayerModel(models.Model):
    player_id = models.AutoField(primary_key=True)
    steam_id3 = models.BigIntegerField(null=True, db_index=True, unique=True)
    name = models.CharField(max_length=100)
    icon = models.JSONField(null=True)
    region = models.CharField(max_length=2, null=True, blank=True)
    private = models.BooleanField(default=False)
    rank = models.IntegerField(default=0)
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, null=True)
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
    guardians = models.IntegerField(null=True)
    walkers = models.IntegerField(null=True)
    baseGuardians = models.IntegerField(null=True)
    shieldGenerators = models.IntegerField(null=True)
    patrons = models.IntegerField(null=True)
    midbosses = models.IntegerField(null=True)
    rejuvinators = models.IntegerField(null=True)
    laneCreeps = models.IntegerField(default=0)
    neutralCreeps = models.IntegerField(default=0)
    lastHits = models.IntegerField(default=0)
    denies = models.IntegerField(default=0)
    multis = models.JSONField(null=True) # [0, 0, 0, 0, 0, 0]
    streaks = models.JSONField(null=True) # [0, 0, 0, 0, 0, 0, 0]
    longestStreak = models.IntegerField(default=0)
    mmr = models.BigIntegerField(default=0)
    lastLogin = models.BigIntegerField(null=True, blank=True)
    timePlayed = models.IntegerField(null=True, blank=True)
    created = models.BigIntegerField(
        default=current_timestamp,
        null=True,
        blank=True
    )
    updated = models.BigIntegerField(null=True)
    isUser = models.BooleanField(default=True) # TODO: Change default to False after testing
    inactive = models.BooleanField(default=False) # TODO: Change default to True after testing

    def __str__(self):
        return self.name

    def isInactive(self):
        if self.lastLogin:
            return time.time() - self.lastLogin > 1296000
        return False # TODO: Change back to True after testing

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
            self.name = playerData[0].get('personaname')
            self.icon = playerData[0].get('avatarfull')
            self.region = playerData[0].get('loccountrycode')

        gameData = steamWebAPI.getOwnedGames(steam_id3=self.steam_id3).get('response').get('games')
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
            lastHits=models.Sum('lastHits'),
            denies=models.Sum('denies'),
            longestStreak=models.Max('longestStreak'),
            accuracy=models.Avg('accuracy'),
            heroCritPercent=models.Avg('heroCritPercent'),
            soulsPerMin=models.Avg('soulsPerMin'),
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
        self.lastHits = stats['lastHits'] or 0
        self.denies = stats['denies'] or 0
        self.longestStreak = max(self.longestStreak or 0, stats.get('longestStreak', 0)) if stats.get('longestStreak') is not None else self.longestStreak or 0
        self.accuracy = round(stats['accuracy'], 4) if stats['accuracy'] is not None else 1
        self.heroCritPercent = round(stats['heroCritPercent'], 4) if stats['heroCritPercent'] is not None else 1
        self.soulsPerMin = round(stats['soulsPerMin'], 4) if stats['soulsPerMin'] is not None else 1


    def updatePlayerStatsFromMatchPlayer(self, team, multis, streaks, longestStreak, objectiveEvents, midbossEvents, match):

        self.longestStreak = max(self.longestStreak, longestStreak)

        for event in midbossEvents:
            if event.team == team:
                self.rejuvinators = self.rejuvinators + 1 if self.rejuvinators else 1
            if event.slayer == team:
                self.midbosses = self.midbosses + 1 if self.midbosses else 1

        # Sketchy way of getting opposite teams
        oppositeTeams = {'k_ECitadelLobbyTeam_Team0': 'k_ECitadelLobbyTeam_Team1',
                         'k_ECitadelLobbyTeam_Team1': 'k_ECitadelLobbyTeam_Team0'}

        for event in objectiveEvents:
            if oppositeTeams[event.team] == team:
                if 'Tier1' in event.target:
                    self.guardians = self.guardians + 1 if self.guardians else 1
                elif 'Tier2' in event.target:
                    self.walkers = self.walkers + 1 if self.walkers else 1
                elif 'BarrackBoss' in event.target:
                    self.baseGuardians = self.baseGuardians + 2 if self.baseGuardians else 2
                elif 'TitanShieldGenerator' in event.target:
                    self.shieldGenerators = self.shieldGenerators + 1 if self.shieldGenerators else 1
                elif 'k_eCitadelTeamObjective_Core' in event.target:
                    self.patrons = self.patrons + 1 if self.patrons else 1


        if any(x != 0 for x in multis):
            if self.multis is None:
                self.multis = multis
            else:
                self.multis = [sum(x) for x in zip(self.multis, multis)]
        if any(x != 0 for x in streaks):
            if self.streaks is None:
                self.streaks = streaks
            else:
                self.streaks = [sum(x) for x in zip(self.streaks, streaks)]

        self.matches.add(match)


    def updatePlayerRecords(self, heroId, kills, assists, souls, heroDamage, objDamage, healing, lastHits):
        if self.isUser and self.isInactive() is False:
            playerRecords = PlayerRecords.objects.filter(player=self).first()
            if not playerRecords:
                playerRecords = PlayerRecords.objects.create(player=self)

            playerRecords.updateRecord('kills', heroId, kills)
            playerRecords.updateRecord('assists', heroId, assists)
            playerRecords.updateRecord('souls', heroId, souls)
            playerRecords.updateRecord('heroDamage', heroId, heroDamage)
            playerRecords.updateRecord('objDamage', heroId, objDamage)
            playerRecords.updateRecord('healing', heroId, healing)
            playerRecords.updateRecord('lastHits', heroId, lastHits)



    def updatePlayerHeroStatsFromMatchPlayer(self, mp, longestStreaks):
        # Update player hero model
        hero = HeroesModel.objects.filter(hero_deadlock_id=mp['hero_deadlock_id']).first()
        if not hero:
            DLAPIAssets = deadlockAPIAssetsService()
            heroName = DLAPIAssets.getHeroAssetsById(mp['hero_deadlock_id']).get('name')
            hero = HeroesModel.objects.create(
                name=heroName,
                hero_deadlock_id=mp['hero_deadlock_id']
            )
        playerHero = PlayerHeroModel.objects.filter(player=self, hero=hero).first()
        if not playerHero:
            playerHero = PlayerHeroModel.objects.create(
                player=self,
                hero=hero
            )

        playerHero.createOrUpdatePlayerHero(mp, longestStreaks)

