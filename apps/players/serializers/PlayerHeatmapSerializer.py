import datetime
from rest_framework import serializers

from ..Models.PlayerModel import PlayerModel

class PlayerHeatmapSerializer(serializers.ModelSerializer):
    dateData = serializers.SerializerMethodField()

    class Meta:
        model = PlayerModel
        fields = ['dateData']

    def get_dateData(self, obj):
        thirty_days_ago = datetime.date.today() - datetime.timedelta(days=30)
        result = []

        for i in range(30):
            current_date = thirty_days_ago + datetime.timedelta(days=i)
            start_of_day = datetime.datetime.combine(current_date, datetime.datetime.min.time()).timestamp()
            end_of_day = datetime.datetime.combine(current_date, datetime.datetime.max.time()).timestamp()

            count = obj.matches.filter(date__gte=start_of_day, date__lte=end_of_day).count()
            result.append({'date': current_date.strftime('%Y-%m-%d'), 'count': count})

        return result