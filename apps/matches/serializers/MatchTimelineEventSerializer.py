from rest_framework import serializers
from apps.matches.Models.MatchTimeline import MatchTimelineEvent, PvPEvent, ObjectiveEvent, MidbossEvent


class MatchTimelineEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchTimelineEvent
        fields = '__all__'


class PvPEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = PvPEvent
        fields = '__all__'


class ObjectiveEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectiveEvent
        fields = '__all__'


class MidbossEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = MidbossEvent
        fields = '__all__'
