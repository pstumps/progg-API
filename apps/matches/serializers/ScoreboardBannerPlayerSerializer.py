from rest_framework import serializers
from apps.matches.Models.MatchPlayerModel import MatchPlayerModel
from apps.heroes.Models.HeroesModel import HeroesModel
from apps.heroes.serializers.RecentMatchStatsHeroSerializer import RecentMatchStatsHeroSerializer



class ScoreboardBannerPlayerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    hero = serializers.SerializerMethodField()
    rank = serializers.SerializerMethodField()

    class Meta:
        model = MatchPlayerModel
        fields = ['name', 'hero', 'rank', 'lane', 'build', 'buildItems', 'kills', 'deaths', 'assists', 'souls', 'heroDmg',
                  'objDmg', 'healing', 'lastHits']

    def get_name(self, obj):
        if obj.player:
            if obj.player.name == None:
                obj.player.updatePlayerFromSteamWebAPI()
                return obj.player.name
            return obj.player.name
        return None

    def get_hero(self, obj):
        hero = HeroesModel.objects.get(hero_deadlock_id=obj.hero_deadlock_id)
        return RecentMatchStatsHeroSerializer(hero).data

    def get_rank(self, obj):
        return None # TODO: Figure out how to get rank

    def get_lane(self, obj):
        return obj.lane



