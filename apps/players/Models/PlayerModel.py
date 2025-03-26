import time
from django.db import models
from django.conf import settings
from proggbackend.services.DeadlockAPIAssets import deadlockAPIAssetsService
from proggbackend.services.SteamWebAPI import SteamWebAPIService
from .PlayerHeroModel import PlayerHeroModel
from .PlayerRecords import PlayerRecords
from ...heroes.Models.HeroesModel import HeroesModel
from ...matches.Models.MatchesModel import MatchesModel

def calculate_average_rank(ranks):
    def rank_to_numeric(r):
        if r == 0:
            return 0
        m = r // 10
        s = r % 10
        return 6*m+s

    valid_ranks = [0] + [6 * m + s for m in range(1, 12) for s in range(1, 7)]
    numeric_ranks = [rank_to_numeric(r) for r in ranks if rank_to_numeric(r) in valid_ranks]
    avg = sum(numeric_ranks) / len(numeric_ranks) if numeric_ranks else 0
    closest = min(valid_ranks, key=lambda x: abs(x - avg))

    if closest == 0:
        return 0
    else:
        main = closest // 6
        sub = closest % 6
        return int(f'{main}{sub}')


def current_timestamp():
    return int(time.time())

def default_multis():
    return [0, 0, 0, 0, 0, 0]

def default_streaks():
    return [0, 0, 0, 0, 0, 0, 0]


class PlayerModel(models.Model):
    player_id = models.AutoField(primary_key=True)
    steam_id3 = models.BigIntegerField(db_index=True, unique=True) #TODO Change from null=True to False after testing
    name = models.CharField(max_length=100)
    icon = models.JSONField(null=True)
    region = models.CharField(max_length=2, null=True, blank=True)
    private = models.BooleanField(default=False)
    rank = models.IntegerField(null=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
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
    multis = models.JSONField(
        default=default_multis,
        null=True) # [0, 0, 0, 0, 0, 0]
    streaks = models.JSONField(
        default=default_streaks,
        null=True) # [0, 0, 0, 0, 0, 0, 0]
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
    inactive = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def calculateRank(self):
        last_ten_matches = self.matches.order_by('-date')[:10]
        if len(last_ten_matches) == 0:
            self.rank = None

        if len(last_ten_matches) == 1:
            single_match = last_ten_matches[0]
            if single_match.averageRank:
                if single_match.averageRank.get('match_average_badge'):
                    self.rank = int(single_match.averageRank.get('match_average_badge'))

        averageRanks = []
        for match in last_ten_matches:
            if match.averageRank:
                if match.averageRank.get('match_average_badge'):
                    averageRanks.append(int(match.averageRank.get('match_average_badge')))

        self.rank = calculate_average_rank(averageRanks)


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
            guardians=models.Sum('guardians'),
            walkers=models.Sum('walkers'),
            baseGuardians=models.Sum('baseGuardians'),
            shieldGenerators=models.Sum('shieldGenerators'),
            patrons=models.Sum('patrons'),
            midbosses=models.Sum('midbosses'),
            rejuvinators=models.Sum('rejuvinators'),
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
        self.guardians = stats['guardians'] or 0
        self.walkers = stats['walkers'] or 0
        self.baseGuardians = stats['baseGuardians'] or 0
        self.shieldGenerators = stats['shieldGenerators'] or 0
        self.patrons = stats['patrons'] or 0
        self.midbosses = stats['midbosses'] or 0
        self.rejuvinators = stats['rejuvinators'] or 0

        multis_list = list(self.player_hero_stats.values_list('multis', flat=True))
        multis_arrays = [m for m in multis_list if m]
        if multis_arrays:
            multis_sum = [sum(x) for x in zip(*multis_arrays)]
        else:
            multis_sum = []
        self.multis = multis_sum

        # TODO: Fix how last streak index is calculated
        streaks_list = list(self.player_hero_stats.values_list('streaks', flat=True))
        streaks_array = [m for m in streaks_list if m]
        if streaks_array:
            streaks_sum = [sum(x) for x in zip(*streaks_array)]
        else:
            streaks_sum = []
        self.streaks = streaks_sum
        self.updated = int(time.time())
        self.calculateRank()
        self.save()


    def updatePlayerRecords(self, matchId, heroId, kills, assists, souls, heroDamage, objDamage, healing, lastHits):
        playerRecords = PlayerRecords.objects.filter(player=self).first()
        if not playerRecords:
            playerRecords = PlayerRecords.objects.create(player=self)

        playerRecords.updateRecord('kills', heroId, kills, matchId)
        playerRecords.updateRecord('assists', heroId, assists, matchId)
        playerRecords.updateRecord('souls', heroId, souls, matchId)
        playerRecords.updateRecord('heroDamage', heroId, heroDamage, matchId)
        playerRecords.updateRecord('objDamage', heroId, objDamage, matchId)
        playerRecords.updateRecord('healing', heroId, healing, matchId)
        playerRecords.updateRecord('lastHits', heroId, lastHits, matchId)

    def getOrCreatePlayerHero(self, heroId):
        # Update player hero model
        hero = HeroesModel.objects.filter(hero_deadlock_id=heroId).first()
        if not hero:
            DLAPIAssets = deadlockAPIAssetsService()
            heroName = DLAPIAssets.getHeroAssetsById(heroId).get('name')
            hero = HeroesModel.objects.create(
                name=heroName,
                hero_deadlock_id=heroId
            )
        playerHero = PlayerHeroModel.objects.filter(player=self, hero=hero).first()
        if not playerHero:
            playerHero = PlayerHeroModel.objects.create(
                player=self,
                hero=hero
            )

        return playerHero


    def addMatch(self, match):
        if match not in self.matches.all():
            self.matches.add(match)
            self.save()

