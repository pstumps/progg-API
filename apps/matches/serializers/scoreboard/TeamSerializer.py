from django.db.models import Sum
from rest_framework import serializers
from apps.matches.Models.MatchesModel import MatchesModel
from apps.matches.serializers.scoreboard.ScoreboardBannerPlayerSerializer import ScoreboardBannerPlayerSerializer


class TeamSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    totalKills = serializers.SerializerMethodField()
    totalHeroDmg = serializers.SerializerMethodField()
    totalObjDmg = serializers.SerializerMethodField()
    totalHealing = serializers.SerializerMethodField()
    averageRank = serializers.SerializerMethodField()
    players = serializers.SerializerMethodField()

    class Meta:
        model = MatchesModel
        fields = ['name', 'totalKills', 'totalHeroDmg', 'totalObjDmg', 'totalHealing', 'averageRank', 'players']

    def get_name(self, obj):
        team_value = self.context.get('team')
        teamDict = {'k_ECitadelLobbyTeam_Team0': 'Amber', 'k_ECitadelLobbyTeam_Team1': 'Sapphire'}
        return teamDict[team_value]

    def get_team_players(self, obj):
        team_value = self.context.get('team')
        if team_value is None:
            raise ValueError("You must pass a 'team' in serializer context")
        return obj.matchPlayerModels.filter(team=team_value)

    def get_totalKills(self, obj):
        team_players = self.get_team_players(obj)
        agg = team_players.aggregate(total=Sum('kills'))
        return agg['total'] or 0

    def get_totalHeroDmg(self, obj):
        team_players = self.get_team_players(obj)
        agg = team_players.aggregate(total=Sum('heroDamage'))
        return agg['total'] or 0

    def get_totalObjDmg(self, obj):
        team_players = self.get_team_players(obj)
        agg = team_players.aggregate(total=Sum('objDamage'))
        return agg['total'] or 0

    def get_totalHealing(self, obj):
        team_players = self.get_team_players(obj)
        agg = team_players.aggregate(total=Sum('healing'))
        return agg['total'] or 0

    def get_averageRank(self, obj):
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
        rank = None
        team_value = self.context.get('team')
        if obj.averageRank:
            if 'Team0' in team_value:
                rank = obj.averageRank.get('average_badge_team0')
            elif 'Team1' in team_value:
                rank = obj.averageRank.get('average_badge_team1')
            else:
                raise ValueError("Invalid team value")

        if rank:
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

    def get_players(self, obj):
        team_players = self.get_team_players(obj)
        return ScoreboardBannerPlayerSerializer(team_players, many=True).data

