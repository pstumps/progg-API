from django.db import models

def default_multis():
    return [0, 0, 0, 0, 0, 0]

def default_streaks():
    return [0, 0, 0, 0, 0, 0, 0]

class PlayerHeroModel(models.Model):
    player_hero_id = models.AutoField(primary_key=True)
    steam_id3 = models.BigIntegerField(null=True)
    player = models.ForeignKey('players.PlayerModel', related_name='player_hero_stats', on_delete=models.SET_NULL, null=True) #TODO Change from null=True to False after testing
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


    def updatePlayerHero(self, matchPlayer, multis, streaks, objectiveEvents, midbossEvents, longestStreak):
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


        for event in midbossEvents:
            if event.team == matchPlayer['team']:
                self.rejuvinators = self.rejuvinators + 1 if self.rejuvinators else 1
            if event.slayer == matchPlayer['team']:
                self.midbosses = self.midbosses + 1 if self.midbosses else 1

        # Sketchy way of getting opposite teams
        oppositeTeams = {'k_ECitadelLobbyTeam_Team0': 'k_ECitadelLobbyTeam_Team1',
                         'k_ECitadelLobbyTeam_Team1': 'k_ECitadelLobbyTeam_Team0'}

        for event in objectiveEvents:
            if oppositeTeams[event.team] == matchPlayer['team']:
                if 'Tier1' in event.target:
                    self.guardians = self.guardians + 1 if self.guardians else 1
                elif 'Tier2' in event.target:
                    self.walkers = self.walkers + 1 if self.walkers else 1
                elif 'BarrackBoss' in event.target:
                    self.baseGuardians = self.baseGuardians + 2 if self.baseGuardians else 2
                elif 'TitanShieldGenerator' in event.target:
                    self.shieldGenerators = self.shieldGenerators + 1 if self.shieldGenerators else 1
                elif 'k_eCitadelTeamObjective_Titan' in event.target:
                    self.titans = self.titans + 1 if self.titans else 1
                elif 'k_eCitadelTeamObjective_Core' in event.target:
                    self.patrons = self.patrons + 1 if self.patrons else 1

        if any(x != 0 for x in multis):
            self.multis = [sum(x) for x in zip(self.multis, multis)]
        if any(x != 0 for x in streaks):
            self.streaks = [sum(x) for x in zip(self.streaks, streaks)]

        self.save()
