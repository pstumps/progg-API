from rest_framework import serializers
from ...matches.serializers.RecentMatchPlayerModelSerializer import RecentMatchPlayerModelSerailizer
from ..Models.PlayerModel import PlayerModel

class PlayerModelSerializer(serializers.ModelSerializer):
    accuracy = serializers.SerializerMethodField()
    critAccuracy = serializers.SerializerMethodField()
    matchesPlayed = serializers.SerializerMethodField()
    lastMatchDate = serializers.SerializerMethodField()
    recentMatches = serializers.SerializerMethodField()
    doubles = serializers.SerializerMethodField()
    triples = serializers.SerializerMethodField()
    quadras = serializers.SerializerMethodField()
    pentas = serializers.SerializerMethodField()
    megas = serializers.SerializerMethodField()
    gigas = serializers.SerializerMethodField()
    threeStreaks = serializers.SerializerMethodField()
    fourStreaks = serializers.SerializerMethodField()
    fiveStreaks = serializers.SerializerMethodField()
    sixStreaks = serializers.SerializerMethodField()
    sevenStreaks = serializers.SerializerMethodField()
    eightStreaks = serializers.SerializerMethodField()
    eightPlusStreaks = serializers.SerializerMethodField()

    class Meta:
        model = PlayerModel
        fields = ['steam_id3', 'name', 'icon', 'region', 'rank', 'wins', 'kills', 'deaths', 'assists', 'souls',
                  'soulsPerMin', 'accuracy', 'critAccuracy', 'heroDamage', 'objDamage', 'healing', 'guardians', 'walkers',
                  'baseGuardians', 'shieldGenerators', 'patrons', 'midbosses', 'rejuvinators', 'laneCreeps',
                  'neutralCreeps', 'lastHits', 'denies', 'longestStreak', 'mmr', 'lastMatchDate',
                  'lastLogin', 'timePlayed', 'created', 'updated', 'matchesPlayed', 'recentMatches', 'doubles',
                  'triples', 'quadras', 'pentas', 'megas', 'gigas', 'threeStreaks', 'fourStreaks', 'fiveStreaks',
                  'sixStreaks', 'sevenStreaks', 'eightStreaks', 'eightPlusStreaks']

    def get_matchesPlayed(self, obj):
        return obj.matches.count()

    def get_lastMatchDate(self, obj):
        return obj.getLastMatch().date

    def get_recentMatches(self, obj):
        recentMatches = []
        for matchPlayerModel in obj.matchPlayerModels.all():
            matchPlayerModel = RecentMatchPlayerModelSerailizer(matchPlayerModel)
            recentMatches.append(matchPlayerModel.data)
        sorted_recentMatches = sorted(recentMatches, key=lambda x: x['date'], reverse=True)
        return sorted_recentMatches

    def get_accuracy(self, obj):
        return round(obj.accuracy * 100, 1)

    def get_critAccuracy(self, obj):
        return round(obj.heroCritPercent * 100, 1)

    def get_doubles(self, obj):
        return obj.multis[0] if obj.multis else 0

    def get_triples(self, obj):
        return obj.multis[1] if obj.multis else 0

    def get_quadras(self, obj):
        return obj.multis[2] if obj.multis else 0

    def get_pentas(self, obj):
        return obj.multis[3] if obj.multis else 0

    def get_megas(self, obj):
        return obj.multis[4] if obj.multis else 0

    def get_gigas(self, obj):
        return obj.multis[5] if obj.multis else 0

    def get_threeStreaks(self, obj):
        return obj.streaks[0] if obj.streaks else 0

    def get_fourStreaks(self, obj):
        return obj.streaks[1] if obj.streaks else 0

    def get_fiveStreaks(self, obj):
        return obj.streaks[2] if obj.streaks else 0

    def get_sixStreaks(self, obj):
        return obj.streaks[3] if obj.streaks else 0

    def get_sevenStreaks(self, obj):
        return obj.streaks[4] if obj.streaks else 0

    def get_eightStreaks(self, obj):
        return obj.streaks[5] if obj.streaks else 0

    def get_eightPlusStreaks(self, obj):
        return obj.streaks[6] if obj.streaks else 0