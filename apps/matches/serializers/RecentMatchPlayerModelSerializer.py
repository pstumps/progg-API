import time

from rest_framework import serializers
from ..Models.MatchPlayerModel import MatchPlayerModel
from ...heroes.serializers import RecentMatchStatsHeroSerializer
from ...heroes.Models.HeroesModel import HeroesModel


class RecentMatchPlayerModelSerailizer(serializers.ModelSerializer):
    team = serializers.SerializerMethodField()
    length = serializers.SerializerMethodField()
    when = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
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
    medals = serializers.SerializerMethodField()

    class Meta:
        model = MatchPlayerModel
        fields = ['team', 'win', 'level', 'length', 'date', 'when', 'lastHits', 'denies', 'accuracy', 'kills', 'deaths',
                  'assists', 'souls', 'hero', 'damage', 'teamobj', 'teamkills', 'teamsouls', 'enemyobj', 'enemykills',
                  'enemysouls', 'build', 'medals', 'party', 'avgRank']

    def get_team(self, obj):
        return 'Amber' if obj.team == 'k_ECitadelLobbyTeam_Team0' else 'Sapphire'

    def get_length(self, obj):
        return int(obj.match.length / 60)

    def get_date(self, obj):
        return int(obj.match.date.timestamp())

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
        uncerealizedHero = HeroesModel.objects.get(hero_deadlock_id=obj.hero_deadlock_id)
        hero = RecentMatchStatsHeroSerializer(uncerealizedHero)
        return hero.data

    def get_damage(self, obj):
        return obj.heroDamage

    def get_accuracy(self, obj):
        return int(obj.accuracy * 100)

    def get_teamobj(self, obj):
        matchStats = obj.match.teamStats
        return matchStats[obj.team].get('objDamage', 0)

    def get_teamkills(self, obj):
        matchStats = obj.match.teamStats
        return matchStats[obj.team].get('kills', 0)

    def get_teamsouls(self, obj):
        matchStats = obj.match.teamStats
        return matchStats[obj.team].get('souls', 0)

    def get_enemyobj(self, obj):
        matchStats = obj.match.teamStats
        enemyTeam = next(team for team in matchStats if team != obj.team)
        return matchStats[enemyTeam].get('objDamage', 0)

    def get_enemykills(self, obj):
        matchStats = obj.match.teamStats
        enemyTeam = next(team for team in matchStats if team != obj.team)
        return matchStats[enemyTeam].get('kills', 0)

    def get_enemysouls(self, obj):
        matchStats = obj.match.teamStats
        enemyTeam = next(team for team in matchStats if team != obj.team)
        return matchStats[enemyTeam].get('souls', 0)

    def get_build(self, obj):
        print(obj.match.deadlock_id)
        build = {'weapon': 0, 'spirit': 0, 'vitality': 0}
        percentArray = []

        for type, items in obj.items.items():
            if type != 'flex':
                build[type] = len(items)
            else:
                for fItem in items:
                    build[fItem['type']] += 1

        for count in build.values():
            filled = min(count, 8)
            percent = round(filled / 8 * 100, 2)
            percentArray.append(percent)

        return percentArray

    def get_avgRank(self, obj):
        if obj.match.matchMode == 'k_ECitadelMatchMode_Unranked':
            return 'Unranked'
        return obj.match.averageRank.get('match_average_badge', 0)

    def get_medals(self, obj):
        if obj.medals:
            return obj.medals
        return []