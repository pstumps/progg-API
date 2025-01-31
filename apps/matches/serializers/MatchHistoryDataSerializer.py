import time

from rest_framework import serializers
from ..Models.MatchPlayerModel import MatchPlayerModel
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

    class Meta:
        model = MatchPlayerModel
        fields = []