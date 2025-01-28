from rest_framework import serializers
from ..matches.serializers import RecentMatchPlayerModelSerailizer
from .Models.PlayerModel import PlayerModel
from .Models.PlayerHeroModel import PlayerHeroModel

class PlayerModelSerializer(serializers.ModelSerializer):
    matchesPlayed = serializers.SerializerMethodField()
    recentMatches = serializers.SerializerMethodField()

    class Meta:
        model = PlayerModel
        fields = '__all__'

    def get_matchesPlayed(self, obj):
        return obj.matches.count()

    def get_recentMatches(self, obj):
        recentMatches = []
        for matchPlayerModel in obj.matchPlayerModels.all():
            matchPlayerModel = RecentMatchPlayerModelSerailizer(matchPlayerModel)
            recentMatches.append(matchPlayerModel.data)
        return recentMatches

class PlayerHeroModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerHeroModel
        fields = '__all__'