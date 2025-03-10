from rest_framework import serializers
from ..Models.PlayerModel import PlayerModel

class SearchHistoryPlayer(serializers.ModelSerializer):
    lastMatchAverageRank = serializers.SerializerMethodField()

    class Meta:
        model = PlayerModel
        fields = ['name', 'steam_id3', 'icon', 'region', 'lastMatchAverageRank']

    def get_lastMatchAverageRank(self, obj):
        lastMatch = obj.getLastMatch()
        averageRank = None
        if lastMatch:
            averageRank = lastMatch.averageRank.get('match_average_badge')

        if averageRank:
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

            if averageRank == 0:
                return {'name': 'Obscurus', 'image': 'http://127.0.0.1/images/ranks/0/base/small.webp'}

            rank_str = str(averageRank)
            main_rank = int(rank_str[:-1])
            sub_rank = int(rank_str[-1])

            if 1 <= main_rank <= 11 and 1 <= sub_rank <= 6:
                return {'name': str(rankDict[int(main_rank)]) + ' ' + str(sub_rank),
                        'image': 'http://127.0.0.1:8080/images/ranks/' + str(main_rank) + '/' + str(sub_rank) + '/' 'small.webp'}
            return None

        return None
