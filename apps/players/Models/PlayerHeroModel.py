from django.db import models
from django.forms.models import model_to_dict

def default_multis():
    return [0, 0, 0, 0, 0, 0]

def default_streaks():
    return [0, 0, 0, 0, 0, 0, 0]

class PlayerHeroModel(models.Model):
    player_hero_id = models.AutoField(primary_key=True)
    steam_id3 = models.BigIntegerField(null=True)
    player = models.ForeignKey('players.PlayerModel', related_name='player_hero_stats', on_delete=models.SET_NULL, null=True) #TODO Change from null=True to False after testing
    hero = models.ForeignKey('heroes.HeroesModel', related_name='player_hero_stats', on_delete=models.CASCADE)
    rank = models.IntegerField(null=True)
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
    multis = models.JSONField(
        default=default_multis,
        null=True) # [0, 0, 0, 0, 0, 0]
    streaks = models.JSONField(
        default=default_streaks,
        null=True) # [0, 0, 0, 0, 0, 0, 0]
    longestStreak = models.IntegerField(default=0)
    guardians = models.IntegerField(default=0)
    walkers = models.IntegerField(default=0)
    baseGuardians = models.IntegerField(default=0)
    shieldGenerators = models.IntegerField(default=0)
    titans = models.IntegerField(default=0)
    patrons = models.IntegerField(default=0)
    midbosses = models.IntegerField(default=0)
    rejuvinators = models.IntegerField(default=0)
    tier = models.IntegerField(null=True)
    beta = models.BooleanField(default=0)

    def __str__(self):
        return self.hero.name


    def updateFromMatchPlayerStats(self, matchPlayer, longestStreak):
        self.steam_id3 = matchPlayer['steam_id3']
        self.wins += 1 if matchPlayer['win'] else 0
        self.matches += 1
        self.kills += matchPlayer['kills']
        self.deaths += matchPlayer['deaths']
        self.assists += matchPlayer['assists']
        self.souls += matchPlayer['souls']
        self.soulsPerMin = (self.soulsPerMin + matchPlayer['soulsPerMin']) / 2
        self.heroDamage += matchPlayer['heroDamage']
        self.objDamage += matchPlayer['objDamage']
        self.healing += matchPlayer['healing']
        self.laneCreeps += matchPlayer['laneCreeps']
        self.neutralCreeps += matchPlayer['neutralCreeps']
        self.lastHits += matchPlayer['lastHits']
        self.denies += matchPlayer['denies']
        self.longestStreak = max(self.longestStreak, longestStreak) if self.longestStreak else longestStreak
        if self.accuracy == 0:
            self.accuracy = matchPlayer['accuracy']
        else:
            self.accuracy = (self.accuracy + matchPlayer['accuracy']) / 2
        if self.heroCritPercent == 0:
            self.heroCritPercent = matchPlayer['heroCritPercent']
        else:
            self.heroCritPercent = (self.heroCritPercent + matchPlayer['heroCritPercent']) / 2


    def updateMultisStreaksStats(self, multis, streaks):
        if any(x != 0 for x in multis):
            self.multis = [sum(x) for x in zip(self.multis, multis)]
        if any(x != 0 for x in streaks):
            self.streaks = [sum(x) for x in zip(self.streaks, streaks)]

    def updateMidbossStats(self, team, midbossEvents):
        for event in midbossEvents:
            if str(event.team) == str(team):
                self.rejuvinators = self.rejuvinators + 1 if self.rejuvinators else 1
            if str(event.slayer) == str(team):
                self.midbosses = self.midbosses + 1 if self.midbosses else 1

    def updateLegacyTeamObjectiveStats(self, team, objectiveEvents):
        oppositeTeams = {'k_ECitadelLobbyTeam_Team0': 'k_ECitadelLobbyTeam_Team1',
                         'k_ECitadelLobbyTeam_Team1': 'k_ECitadelLobbyTeam_Team0',
                         '0': '1',
                         '1': '0',
                         'Team0': 'Team1',
                         'Team1': 'Team0'}

        for event in objectiveEvents:
            if oppositeTeams[str(event.team)] == team:
                if 'Tier1' in event.target:
                    self.guardians = self.guardians + 1 if self.guardians else 1
                elif 'Tier2' in event.target:
                    self.walkers = self.walkers + 1 if self.walkers else 1
                elif 'BarrackBoss' in event.target:
                    self.baseGuardians = self.baseGuardians + 2 if self.baseGuardians else 2
                elif 'TitanShieldGenerator' in event.target:
                    self.shieldGenerators = self.shieldGenerators + 1 if self.shieldGenerators else 1
                elif 'Titan' in event.target:
                    self.titans = self.titans + 1 if self.titans else 1
                elif 'Core' in event.target:
                    self.patrons = self.patrons + 1 if self.patrons else 1

    def updateTeamObjectiveStats(self, team, objectiveEvents):
        oppositeTeams = {'k_ECitadelLobbyTeam_Team0': 'k_ECitadelLobbyTeam_Team1',
                         'k_ECitadelLobbyTeam_Team1': 'k_ECitadelLobbyTeam_Team0',
                         '0': '1',
                         '1': '0',
                         'Team0': 'Team1',
                         'Team1': 'Team0'}

        for event in objectiveEvents:
            if oppositeTeams[str(event.team)] == team:
                target = int(event.target)
                if target == 1 or target == 3 or target == 4:
                    self.guardians = self.guardians + 1 if self.guardians else 1
                if target == 5 or target == 7 or target == 8:
                    self.walkers = self.walkers + 1 if self.walkers else 1
                if target == 9 or target == 10 or target == 11 or target == 12 or target == 13:
                    self.baseGuardians = self.baseGuardians + 2 if self.baseGuardians else 2
                if target == 14 or target == 15:
                    self.shieldGenerators = self.shieldGenerators + 1 if self.shieldGenerators else 1
                if target == 0:
                    self.patrons = self.patrons + 1 if self.patrons else 1
