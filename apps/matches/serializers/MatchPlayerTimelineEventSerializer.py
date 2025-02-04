from rest_framework import serializers
from apps.matches.Models.MatchPlayerTimeline import MatchPlayerTimelineEvent


class MatchPlayerTimelineEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchPlayerTimelineEvent
        fields = '__all__'


class MatchPlayerTimelineItemEventSerializer(MatchPlayerTimelineEventSerializer):
    class Meta:
        model = MatchPlayerTimelineEvent
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if 'sold_time_s' in instance.details:
            original_representation = representation.copy()
            original_representation['type'] = 'item'
            original_representation['details'] = {'target': instance.details['target']}

            sell_representation = representation.copy()
            sell_representation['type'] = 'sell'
            sell_representation['timestamp'] = instance.details['sold_time_s']
            sell_representation['details'] = {'target': instance.details['target']}

            return [original_representation, sell_representation]
        return representation


