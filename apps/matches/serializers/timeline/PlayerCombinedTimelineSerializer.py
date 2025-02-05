from rest_framework import serializers
from django.db.models import Q
from apps.matches.Models.MatchTimeline import PvPEvent, ObjectiveEvent, MidbossEvent
from apps.matches.Models.MatchPlayerTimeline import MatchPlayerTimelineEvent
from apps.matches.serializers.event.MatchPlayerTimelineEventSerializer import MatchPlayerTimelineEventSerializer, MatchPlayerTimelineItemEventSerializer


class PlayerCombinedTimelineSerializer(serializers.Serializer):
    events = serializers.SerializerMethodField()
    heroID = serializers.IntegerField()

    def get_events(self, obj):
        match = obj
        heroID = self.context.get('heroID')
        player_pvp_events = list(PvPEvent.objects.filter(Q(match=match) & Q(slayer_hero_id=heroID) | Q(victim_hero_id=heroID)))
        objective_events = list(ObjectiveEvent.objects.filter(match=match))
        midboss_events = list(MidbossEvent.objects.filter(match=match))
        player_timeline_events = list(MatchPlayerTimelineEvent.objects.filter(match=match))

        all_events = player_pvp_events + objective_events + midboss_events + player_timeline_events
        #all_events.sort(key=lambda x: x['timestamp'] if isinstance(x, dict) else x.timestamp)

        serialized_events = []
        for event in all_events:
            if isinstance(event, dict):
                serialized_events.append(event)
            else:
                if isinstance(event, MatchPlayerTimelineEvent):
                    if event.type == 'item':
                        serializer = MatchPlayerTimelineItemEventSerializer(event)
                        event_data = serializer.data
                        if isinstance(event_data, list):
                            serialized_events.extend(event_data)
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
