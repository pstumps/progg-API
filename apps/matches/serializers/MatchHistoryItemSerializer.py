from rest_framework import serializers
from apps.matches.Models.MatchesModel import MatchesModel
from django.conf import settings
BASE_IMAGE_URL=settings.BASE_IMAGE_URL

class MatchHistoryItemSerializer(serializers.ModelSerializer):
    AH_team = serializers.SerializerMethodField()
    SF_team = serializers.SerializerMethodField()
    average_rank = serializers.SerializerMethodField()

    class Meta:
        model = MatchesModel
        fields = ['deadlock_id', 'length', 'date', 'AH_team', 'SF_team', 'victor', 'average_rank']

    def get_AH_team(self, instance):
        mps = instance.matchPlayerModels.filter(team__contains='0')
        return [mp.hero_deadlock_id for mp in mps]

    def get_SF_team(self, instance):
        mps = instance.matchPlayerModels.filter(team__contains='1')
        return [mp.hero_deadlock_id for mp in mps]

    def get_average_rank(self, instance):
        averageRank = instance.averageRank.get('match_average_badge')
        if averageRank:
            if averageRank == 0:
                return f'{BASE_IMAGE_URL}/ranks/0/base/small.webp'

            rank_str = str(averageRank)
            main_rank = int(rank_str[:-1])
            sub_rank = int(rank_str[-1])

            if 1 <= main_rank <= 11 and 1 <= sub_rank <= 6:
                return f'{BASE_IMAGE_URL}/ranks/' + str(main_rank) + '/' + str(sub_rank) + '/' 'small.webp'
            return None

        return None


