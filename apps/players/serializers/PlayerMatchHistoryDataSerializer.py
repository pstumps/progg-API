from django.db.models import Sum
from rest_framework import serializers
from ..Models.PlayerModel import PlayerModel
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
    class Meta:
        model = PlayerModel
        fields = []

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        matchPlayerModels = obj.matchPlayerModels.select_related('match').order_by('-match__date')[:20]
        heroes = {}

        aggregated = matchPlayerModels.aggregate(
            wins=Sum('win'),
            kills=Sum('kills'),
            deaths=Sum('deaths'),
            assists=Sum('assists'),
            heroDmg=Sum('heroDamage'),
            objDmg=Sum('objDamage'),
            healing=Sum('healing'),
            soulsPerMin=Sum('soulsPerMin'),
        )

        totalTeamKills = 0
        playerKills = aggregated['kills'] or 0

        for matchPlayer in matchPlayerModels:
            team = matchPlayer.team
            match = matchPlayer.match
            teamKills = match.teamStats.get(str(team), {}).get('kills', 0)
            totalTeamKills += teamKills

            heroes.setdefault(matchPlayer.hero_deadlock_id, {'matches': 0, 'wins': 0, 'kills': 0, 'deaths': 0, 'assists': 0})
            heroes[matchPlayer.hero_deadlock_id]['matches'] += 1
            heroes[matchPlayer.hero_deadlock_id]['wins'] += 1 if matchPlayer.win else 0
            heroes[matchPlayer.hero_deadlock_id]['kills'] += matchPlayer.kills
            heroes[matchPlayer.hero_deadlock_id]['deaths'] += matchPlayer.deaths
            heroes[matchPlayer.hero_deadlock_id]['assists'] += matchPlayer.assists

        killp = (playerKills / totalTeamKills) if totalTeamKills > 0 else 0
        bestChamps = []

        for k, v in sorted(heroes.items(), key=lambda x: x[1]['wins']/x[1]['matches'], reverse=True)[:3]:
            hero = HeroesModel.objects.get(hero_deadlock_id=k)
            bestChamps.append({'name': hero.name,
                               'image': hero.images['icon_hero_card'],
                               'wins': v['wins'],
                               'losses': v['matches'] - v['wins'],
                               'kda': (v['kills'] + v['assists']) / v['deaths'] if v['deaths'] > 0 else 0
                               })


        matchCount = matchPlayerModels.count() or 1
        losses = 20 - aggregated['wins']
        representation.update({
            'wins': aggregated['wins'] or 0,
            'losses': losses if losses > 0 else 0,
            'kills': playerKills / matchCount,
            'deaths': (aggregated['deaths'] or 0) / matchCount,
            'assists': (aggregated['assists'] or 0) / matchCount,
            'killp': killp,
            'heroDmg': (aggregated['heroDmg'] or 0) / matchCount,
            'objDmg': (aggregated['objDmg'] or 0) / matchCount,
            'healing': (aggregated['healing'] or 0) / matchCount,
            'soulsPerMin': (aggregated['soulsPerMin'] or 0) / matchCount,
            'bestChamp': bestChamps
        })

        return representation
