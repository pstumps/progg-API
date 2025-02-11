from rest_framework import serializers
from apps.matches.Models.MatchPlayerTimeline import MatchPlayerTimelineEvent


class MatchPlayerTimelineEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchPlayerTimelineEvent
        fields = '__all__'


class AbilityEventSerializer(MatchPlayerTimelineEventSerializer):
    details = serializers.SerializerMethodField()
    class Meta:
        model = MatchPlayerTimelineEvent
        fields = ['type', 'timestamp', 'details']

    def get_details(self, instance):
        return {'target': instance.details['target'].replace(' ', '')}



class BuyEventSerializer(MatchPlayerTimelineEventSerializer):
    details = serializers.SerializerMethodField()
    class Meta:
        model = MatchPlayerTimelineEvent
        fields = ['type', 'timestamp', 'details']


    def get_details(self, instance):
        if instance.details['slot'] == 'weapon':
            return {'color': 'orange', 'target': instance.details['target'].replace(' ', '_')}
        elif instance.details['slot'] == 'vitality':
            return {'color': 'green', 'target': instance.details['target'].replace(' ', '_')}
        elif instance.details['slot'] == 'spirit':
            return {'color': 'purple', 'target': instance.details['target'].replace(' ', '_')}


class SellEventSerializer(MatchPlayerTimelineEventSerializer):
    type = serializers.SerializerMethodField()
    timestamp = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()
    class Meta:
        model = MatchPlayerTimelineEvent
        fields = ['type', 'timestamp', 'details']

    def get_type(self, instance):
        return 'sell'

    def get_timestamp(self, instance):
        return instance.details['sold_time_s']

    def get_details(self, instance):
        return {'target': instance.details['target']}


