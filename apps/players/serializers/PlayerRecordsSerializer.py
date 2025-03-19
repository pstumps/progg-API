from rest_framework import serializers

from ..Models.PlayerModel import PlayerModel
from ..Models.PlayerRecords import PlayerRecords

class PlayerRecordsSerializer(serializers.ModelSerializer):
    kills = serializers.SerializerMethodField()
    assists = serializers.SerializerMethodField()
    heroDmg = serializers.SerializerMethodField()
    objDmg = serializers.SerializerMethodField()
    healing = serializers.SerializerMethodField()
    souls = serializers.SerializerMethodField()
    class Meta:
        model = PlayerRecords
        fields = ['kills', 'assists', 'heroDmg', 'objDmg', 'healing', 'souls']


    def get_kills(self, obj):
        rec = obj.records['kills']