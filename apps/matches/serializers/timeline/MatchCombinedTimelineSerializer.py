from rest_framework import serializers
from apps.matches.Models.MatchTimeline import PvPEvent, ObjectiveEvent, MidbossEvent
from apps.matches.serializers.event.MatchTimelineEventSerializer import MatchTimelineEventSerializer, PvPEventSerializer, ObjectiveEventSerializer, MidbossEventSerializer, RejuvEventSerializer

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
                pvpEvent = PvPEventSerializer(event).data
                serializedEvents.append(pvpEvent)
            elif isinstance(event, ObjectiveEvent):
                if event.timestamp == 0:
                    continue
                else:
                    objEvent = ObjectiveEventSerializer(event).data
                    serializedEvents.append(objEvent)
            elif isinstance(event, MidbossEvent):
                if event.slayer:
                    midbossEvent = MidbossEventSerializer(event).data
                    rejuvEvent = RejuvEventSerializer(event).data
                    serializedEvents.extend([midbossEvent, rejuvEvent])
                else:
                    midbossEvent = MidbossEventSerializer(event).data
                    serializedEvents.append(midbossEvent)
            else:
                timelineEvent = MatchTimelineEventSerializer(event).data
                serializedEvents.append(timelineEvent)


        return serializedEvents
