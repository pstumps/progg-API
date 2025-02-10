from rest_framework import serializers
from .Models.HeroesModel import HeroesModel

class HeroSerializer(serializers.ModelSerializer):
    winrate = serializers.SerializerMethodField()
    kda = serializers.SerializerMethodField()

    class Meta:
        model = HeroesModel
        fields = ['name', 'tier', 'winrate', 'kda', 'pickrate', 'beta', 'abilities']

    def getWinrate(self, obj):
        return self.calculateWinrate(obj.wins, obj.losses)

    def getKDA(self, obj):
        self.calculateKDA(obj.kills, obj.deaths, obj.assists)

    def calculateWinrate(self, wins, losses):
        winrate = (wins / wins + losses) * 100
        return round(winrate, 1)

    def calculateKDA(self, kills, deaths, assists):
        return round(((kills + assists) / deaths), 2)

class RecentMatchStatsHeroSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = HeroesModel
        fields = ['name', 'image']

    def get_image(self, obj):
        return obj.images['icon_hero_card']
