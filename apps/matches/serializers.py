import datetime, time

from rest_framework import serializers
from .models import MatchesModel
from .models import MatchPlayerModel

from ..heroes.services import HeroesDict


class MatchModelSerailizer(serializers.ModelSerializer):
    class Meta:
        model = MatchesModel
        fields = '__all__'


class MatchPlayerModelSerailizer(serializers.ModelSerializer):
    csSouls = serializers.IntegerField()
    kaSouls = serializers.IntegerField()
    otherSouls = serializers.IntegerField()
    avgHeroDmg = serializers.IntegerField()
    avgObjDmg = serializers.IntegerField()
    avgHealing = serializers.IntegerField()
    avgKills = serializers.IntegerField()
    avgAssists = serializers.IntegerField()
    avgDeaths = serializers.IntegerField()
    avgSouls = serializers.IntegerField()
    avgCS = serializers.IntegerField()
    avgSoulsPerMin = serializers.FloatField()


    class Meta:
        model = MatchPlayerModel
        fields = '__all__'


    def get_csSouls(self, obj):
        totalSouls = obj.soulsBreakdown
        csSouls = totalSouls.get('lane_creeps', 0) + totalSouls.get('neutrals', 0) + totalSouls.get('denies', 0)
        return csSouls

    def get_kaSouls(self, obj):
        totalSouls = obj.soulsBreakdown
        kaSouls = totalSouls.get('hero', 0) + totalSouls.get('assists', 0)
        return kaSouls

    def get_otherSouls(self, obj):
        totalSouls = obj.soulsBreakdown
        otherSouls = totalSouls.get('other', 0) + totalSouls.get('objectives', 0) + totalSouls.get('crates', 0)

        return otherSouls

    def get_avgHeroDmg(self, obj):
        total_hero_damage = obj.player.heroDamage
        total_matches = obj.player.matches.count()
        if total_matches > 0:
            return total_hero_damage / total_matches
        return 0

    def get_avgObjDmg(self, obj):
        total_obj_damage = obj.player.objDamage
        total_matches = obj.player.matches.count()
        if total_matches > 0:
            return total_obj_damage / total_matches
        return 0

    def get_avgHealing(self, obj):
        total_healing = obj.player.healing
        total_matches = obj.player.matches.count()
        if total_matches > 0:
            return total_healing / total_matches
        return 0

    def get_avgKills(self, obj):
        total_kills = obj.player.kills
        total_matches = obj.player.matches.count()
        if total_matches > 0:
            return total_kills / total_matches
        return 0

    def get_avgAssists(self, obj):
        total_assists = obj.player.assists
        total_matches = obj.player.matches.count()
        if total_matches > 0:
            return total_assists / total_matches
        return 0

    def get_avgDeaths(self, obj):
        total_deaths = obj.player.deaths
        total_matches = obj.player.matches.count()
        if total_matches > 0:
            return total_deaths / total_matches
        return 0

    def get_avgSouls(self, obj):
        total_souls = obj.player.souls
        total_matches = obj.player.matches.count()
        if total_matches > 0:
            return total_souls / total_matches
        return 0

    def get_avgCS(self, obj):
        total_cs = obj.player.lastHits
        total_matches = obj.player.matches.count()
        if total_matches > 0:
            return total_cs / total_matches
        return 0

    def get_avgSoulsPerMin(self, obj):
        return obj.player.soulsPerMin


class RecentMatchPlayerModelSerailizer(serializers.ModelSerializer):
    team = serializers.SerializerMethodField()
    length = serializers.SerializerMethodField()
    when = serializers.SerializerMethodField()
    hero = serializers.SerializerMethodField()
    accuracy = serializers.SerializerMethodField()
    damage = serializers.SerializerMethodField()
    teamobj = serializers.SerializerMethodField()
    teamkills = serializers.SerializerMethodField()
    teamsouls = serializers.SerializerMethodField()
    enemyobj = serializers.SerializerMethodField()
    enemykills = serializers.SerializerMethodField()
    enemysouls = serializers.SerializerMethodField()
    build = serializers.SerializerMethodField()
    avgRank = serializers.SerializerMethodField()

    class Meta:
        model = MatchPlayerModel
        fields = ['team', 'win', 'level', 'length', 'when', 'lastHits', 'denies', 'accuracy', 'kills', 'deaths',
                  'assists', 'souls', 'hero', 'damage', 'teamobj', 'teamkills', 'teamsouls', 'enemyobj', 'enemykills',
                  'enemysouls', 'build', 'medals', 'party', 'avgRank']

    def get_team(self, obj):
        return 'Amber' if obj.team == 'k_ECitadelLobbyTeam_Team0' else 'Sapphire'

    def get_length(self, obj):
        return int(obj.match.length / 60)

    def get_when(self, obj):
        last = int(time.time()) - int(obj.match.date.timestamp())

        if last < 60:
            return f"{last} seconds "
        elif last < 3600:
            return f"{last // 60} mins "
        elif last < 86400:
            return f"{last // 3600} hours "
        else:
            return f"{last // 86400} days "

    def get_hero(self, obj):
        return HeroesDict[obj.hero_deadlock_id].lower()

    def get_damage(self, obj):
        return obj.heroDamage

    def get_accuracy(self, obj):
        return int(obj.accuracy * 100)

    def get_teamobj(self, obj):
        matchStats = obj.match.teamStats
        return matchStats[obj.team]['objDamage']

    def get_teamkills(self, obj):
        matchStats = obj.match.teamStats
        return matchStats[obj.team]['kills']

    def get_teamsouls(self, obj):
        matchStats = obj.match.teamStats
        return matchStats[obj.team]['souls']

    def get_enemyobj(self, obj):
        matchStats = obj.match.teamStats
        enemyTeam = next(team for team in matchStats if team != obj.team)
        return matchStats[enemyTeam]['objDamage']

    def get_enemykills(self, obj):
        matchStats = obj.match.teamStats
        enemyTeam = next(team for team in matchStats if team != obj.team)
        return matchStats[enemyTeam]['kills']

    def get_enemysouls(self, obj):
        matchStats = obj.match.teamStats
        enemyTeam = next(team for team in matchStats if team != obj.team)
        return matchStats[enemyTeam]['souls']

    def get_build(self, obj):
        build = {'weapon': 0, 'spirit': 0, 'vitality': 0}
        percentArray = []
        totalItems = 0

        for type, items in obj.items.items():
            if type != 'flex':
                build[type] = len(items)
                totalItems += len(items)
            if type == 'flex':
                for flexItems in items:
                    build[flexItems['type']] += 1
                    totalItems += 1
        for num in build.values():
            percentArray.append(round(num / totalItems, 2))
        return percentArray

    def get_avgRank(self, obj):
        return obj.match.averageRank['match_average_badge']

