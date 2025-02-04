from rest_framework import serializers
from apps.matches.Models.MatchTimeline import MatchTimelineEvent, PvPEvent, ObjectiveEvent, MidbossEvent
from apps.matches.Models.MatchPlayerTimeline import MatchPlayerTimelineEvent
from apps.matches.serializers.MatchTimelineEventSerializer import MatchTimelineEventSerializer
from apps.matches.serializers.MatchPlayerTimelineEventSerializer import MatchPlayerTimelineEventSerializer, MatchPlayerTimelineItemEventSerializer
from apps.matches.serializers.MatchCombinedTimelineSerializer import MatchCombinedTimelineSerializer

class PlayerCombinedTimelineSerializer(MatchCombinedTimelineSerializer):
    events = serializers.SerializerMethodField()
    heroID = serializers.IntegerField()

    def get_events(self, obj):
        match = obj
        heroID = self.context.get('heroID')
        timeline_events = super().get_events(obj)
        player_timeline_events = list(MatchPlayerTimelineEvent.objects.filter(match=match))

        all_events = timeline_events + player_timeline_events
        all_events.sort(key=lambda x: x['timestamp'] if isinstance(x, dict) else x.timestamp)

        serialized_events = []
        for event in all_events:
            if isinstance(event, dict):
                serialized_events.append(event)
            else:
                if isinstance(event, MatchPlayerTimelineEvent):
                    if event.type == 'item':
                        serializer = MatchPlayerTimelineItemEventSerializer(event)
                        event_data = serializer.data
                    else:
                        serializer = MatchPlayerTimelineEventSerializer(event)
                        event_data = serializer.data
                else:
                    continue
                serialized_events.append(event_data)

        for event in serialized_events:
            if 'slayer_hero_id' in event and event['slayer_hero_id'] == heroID:
                event['type'] = 'slay'
            elif 'victim_hero_id' in event and event['victim_hero_id'] == heroID:
                event['type'] = 'death'

        return serialized_events
