import math
from datetime import datetime, timezone
from rest_framework import serializers
from apps.matches.Models.MatchesModel import MatchesModel
from apps.matches.serializers.scoreboard.TeamSerializer import TeamSerializer

class MatchScoreboardSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    result = serializers.SerializerMethodField()
    matchType = serializers.SerializerMethodField()
    overallAverageRank = serializers.SerializerMethodField()
    teams = serializers.SerializerMethodField()
    matchEvents = serializers.SerializerMethodField()
    graphData = serializers.SerializerMethodField()

    class Meta:
        model = MatchesModel
        fields = ['date', 'result', 'matchType', 'length', 'overallAverageRank', 'teams', 'matchEvents', 'graphData']


    def get_date(self, obj):
        return datetime.fromtimestamp(obj.date, timezone.utc)

    def get_result(self, obj):
        if '0' in obj.victor:
            team = 'Amber Hand'
        elif '1' in obj.victor:
            team = 'Sapphire Flame'
        else:
            team = obj.victor
        return team

    def get_matchType(self, obj):
        if obj.matchMode == 'k_ECitadelMatchMode_Unranked':
            return 'Unranked'
        else:
            return 'Ranked'

    def get_overallAverageRank(self, obj):
        if obj.averageRank:
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
            rank = obj.averageRank.get('match_average_badge', None)

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

    def get_teams(self, obj):
        teams = []
        for team in obj.matchPlayerModels.values('team').distinct():
            team_serializer = TeamSerializer(obj, context={'team': team['team']})
            teams.append(team_serializer.data)
        return teams

    def get_matchEvents(self, obj):
        return self.context.get('matchEvents')

    def get_graphData(self, obj):
        return self.context.get('graphData')


