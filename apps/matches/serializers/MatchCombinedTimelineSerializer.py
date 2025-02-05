from rest_framework import serializers
from apps.matches.Models.MatchTimeline import MatchTimelineEvent, PvPEvent, ObjectiveEvent, MidbossEvent
from apps.matches.serializers.MatchTimelineEventSerializer import MatchTimelineEventSerializer, PvPEventSerializer, ObjectiveEventSerializer, MidbossEventSerializer

class MatchCombinedTimelineSerializer(serializers.Serializer):
    events = serializers.SerializerMethodField()

    def get_events(self, obj):
        match = obj
        pvp_events = list(PvPEvent.objects.filter(match=match))
        objective_events = list(ObjectiveEvent.objects.filter(match=match))
        midboss_events = list(MidbossEvent.objects.filter(match=match))
        timelineEvents = sorted(pvp_events + objective_events + midboss_events, key=lambda x: x.timestamp)

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
                eventData = serializer.data
            serializedEvents.append(eventData)

        return serializedEvents
