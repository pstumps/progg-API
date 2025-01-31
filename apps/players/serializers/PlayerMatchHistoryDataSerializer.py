import time
from django.db.models import Sum, Count, F, FloatField

from rest_framework import serializers
from ..Models.PlayerModel import PlayerModel
from ...matches.Models.MatchPlayerModel import MatchPlayerModel
from ...heroes.serializers import RecentMatchStatsHeroSerializer
from ...heroes.Models.HeroesModel import HeroesModel

'''
Match History Data datatype
export interface matchHistoryData { 
    wins: number; // sum of all "1" in 20 generated RecentMatchStats
    losses: number; // sum of all "0" in 20 generated RecentMatchStats
    kills: number; // sum of all kills 20 generated RecentMatchStats
    deaths: number; // sum of all deaths 20 generated RecentMatchStats
    assists: number; // sum of all assists 20 generated RecentMatchStats
    killp: number; // sum of all kills / sum of all teamkills 
    heroDmg: number; // random number between 100,000 and 600000
    objDmg: number; // random number between 60000 and 240000
    healing: number; // random number between 100000 and 400000
    soulsPerMin: number;
    bestChamp: championData[]; // 3 randomly generated championData
}
'''

class MatchHistoryDataSerializer(serializers.ModelSerializer):
    wins = serializers.SerializerMethodField()
    losses = serializers.SerializerMethodField()
    kills = serializers.SerializerMethodField()
    deaths = serializers.SerializerMethodField()
    assists = serializers.SerializerMethodField()
    killp = serializers.SerializerMethodField()
    heroDmg = serializers.SerializerMethodField()
    objDmg = serializers.SerializerMethodField()
    healing = serializers.SerializerMethodField()
    soulsPerMin = serializers.SerializerMethodField()
    bestChamp = serializers.SerializerMethodField()

    class Meta:
        model = PlayerModel
        fields = ['wins', 'losses', 'kills', 'deaths', 'assists', 'killp', 'heroDmg', 'healing', 'soulsPerMin',
                  'bestChamp']

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        matchPlayerModels = obj.matchPlayerModels_set.select_related('match').order_by('-match__date')[:20]
        heroes = {}

        aggregated = matchPlayerModels.aggregate(
            wins=Sum('win'),
            losses=Count('id') - Sum('win'),
            kills=Sum('kills'),
            deaths=Sum('deaths'),
            assists=Sum('assists'),
            heroDmg=Sum('heroDamage'),
            objDmg=Sum('objDamage'),
            healing=Sum('healing'),
        )

        totalTeamKills = 0
        playerKills = aggregated['kills'] or 0

        for matchPlayer in matchPlayerModels:
            team = matchPlayer.team
            match = matchPlayer.match
            teamKills = match.teamStats.get(str(team), {}).get('kills', 0)
            totalTeamKills += teamKills

            if not heroes.get(matchPlayer.hero_deadlock_id):
                heroes[matchPlayer.hero_deadlock_id] = {'wins': 0, 'matches': 0}

            heroes[matchPlayer.hero_deadlock_id]['matches'] += 1
            heroes[matchPlayer.hero_deadlock_id]['wins'] += 1 if matchPlayer.win else 0


        killp = (playerKills / totalTeamKills) if totalTeamKills > 0 else 0

        matchCount = matchPlayerModels.count()
        representation.update({
            'wins': aggregated['wins'],
            'losses': aggregated['losses'],
            'kills': playerKills / matchCount if matchCount > 0 else 0,
            'deaths': aggregated['deaths'] / matchCount if matchCount > 0 else 0,
            'assists': aggregated['assists'] / matchCount if matchCount > 0 else 0,
            'killp': killp,
            'heroDmg': aggregated['heroDmg'] / matchCount if matchCount > 0 else 0,
            'objDmg': aggregated['objDmg'] / matchCount if matchCount > 0 else 0,
            'healing': aggregated['healing'] / matchCount if matchCount > 0 else 0,
            'soulsPerMin': obj.soulsPerMin,
            'bestChamp': sorted(heroes.items(), key=lambda x: x['wins']/x['matches'])
        })
