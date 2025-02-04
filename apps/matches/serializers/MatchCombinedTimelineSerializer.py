from rest_framework import serializers
from apps.matches.Models.MatchTimeline import MatchTimelineEvent, PvPEvent, ObjectiveEvent, MidbossEvent
from apps.matches.serializers.MatchTimelineEventSerializer import MatchTimelineEventSerializer, PvPEventSerializer, ObjectiveEventSerializer, MidbossEventSerializer

class MatchCombinedTimelineSerializer(serializers.Serializer):
    events = serializers.SerializerMethodField()

    def get_events(self, obj):
        match = obj
        timelineEvents = list(MatchTimelineEvent.objects.filter(match=match))
        timelineEvents.sort(key=lambda x: x.timestamp)

        serializedEvents = []
        for event in timelineEvents:
            if isinstance(event, PvPEvent):
                serializer = PvPEventSerializer(event)
                eventData = serializer.data
                eventData['type'] = 'pvp'
            elif isinstance(event, ObjectiveEvent):
                serializer = ObjectiveEventSerializer(event)
                eventData = serializer.data
                eventData['type'] = 'obj'
            elif isinstance(event, MidbossEvent):
                serializer = MidbossEventSerializer(event)
                eventData = serializer.data
                eventData['type'] = 'midboss'
            else:
                serializer = MatchTimelineEventSerializer(event)
            serializedEvents.append(serializer.data)

        return serializedEvents
