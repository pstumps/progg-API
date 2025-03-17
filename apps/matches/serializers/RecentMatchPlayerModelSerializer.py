import time

from rest_framework import serializers
from ..Models.MatchPlayerModel import MatchPlayerModel
from ...heroes.serializers import RecentMatchStatsHeroSerializer
from ...heroes.Models.HeroesModel import HeroesModel
from proggbackend.services.DeadlockAPIAssets import deadlockAPIAssetsService


class RecentMatchPlayerModelSerializer(serializers.ModelSerializer):
    deadlock_id = serializers.SerializerMethodField()
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
        fields = ['deadlock_id', 'team', 'win', 'level', 'length', 'date', 'when', 'lastHits', 'denies', 'accuracy', 'kills', 'deaths',
                  'assists', 'souls', 'hero', 'damage', 'teamobj', 'teamkills', 'teamsouls', 'enemyobj', 'enemykills',
                  'enemysouls', 'build', 'medals', 'party', 'avgRank']

    def get_deadlock_id(self, obj):
        return obj.match.deadlock_id

    def get_team(self, obj):
        return 'Amber' if obj.team == 'k_ECitadelLobbyTeam_Team0' else 'Sapphire'

    def get_length(self, obj):
        return int(obj.match.length / 60)

    def get_date(self, obj):
        return int(obj.match.date)

    def get_when(self, obj):
        last = int(time.time()) - int(obj.match.date)

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
        return obj.items['percentages']

    def get_avgRank(self, obj):
        if obj.match.averageRank:
            rankDict = {
                0: 'Obscurus',
                1: 'Initiate',
                2: 'Seeker',
                3: 'Alchemist',
                4: 'Arcanist',
                5: 'Ritualist',
                6: 'Emissary',
                7: 'Archon',
                8: 'Oracle',
                9: 'Phantom',
                10: 'Ascendant',
                11: 'Eternus'
            }
            rank = obj.match.averageRank.get('match_average_badge', None)

            if rank is not None:
                if rank == 0:
                    return {'name': 'Obscurus', 'image': 'http://127.0.0.1/images/ranks/0/base/small.webp'}
                rank_str = str(rank)
                if len(rank_str) == 2:
                    first_part = rank_str[0]
                    second_part = rank_str[1]
                elif len(rank_str) == 3:
                    first_part = rank_str[:2]
                    second_part = rank_str[2]
                else:
                    raise ValueError("Rank should be either a 2 digit or 3 digit number")
            else:
                first_part = None
                second_part = None

            if first_part is not None and second_part is not None:
                return {'name': rankDict[int(first_part)] + ' ' + second_part,
                        'image': 'http://127.0.0.1:8080/images/ranks/' + first_part + '/' + second_part + '/' 'small.webp'}
            return None

    def get_medals(self, obj):
        if obj.medals:
            return obj.medals
        return []