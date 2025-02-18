from rest_framework import serializers
from apps.matches.Models.MatchTimeline import MatchTimelineEvent, PvPEvent, ObjectiveEvent, MidbossEvent


class MatchTimelineEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchTimelineEvent
        fields = '__all__'


class PvPEventSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()
    class Meta:
        model = PvPEvent
        fields = ['type', 'timestamp', 'details']

    def get_type(self, instance):
        return 'pvp'

    def get_details(self, instance):
        return {'slayer': instance.slayer_hero_id, 'target': instance.victim_hero_id}


class ObjectiveEventSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()
    class Meta:
        model = ObjectiveEvent
        fields = ['type', 'timestamp', 'team', 'details']

    def get_type(self, instance):
        return 'obj'

    def get_details(self, instance):
        target = instance.target.split('_')
        tier = target[2] if len(target) > 2 else None
        lane = target[3] if len(target) > 3 else None
        if lane:
            if lane == 'Lane1':
                lane = 1
            elif lane == 'Lane2':
                lane = 2
            elif lane == 'Lane3':
                lane = 3
            elif lane == 'Lane4':
                lane = 4

        if tier:
            if tier == 'Tier1':
                tier = 1
            elif tier == 'Tier2':
                tier = 2

        if 'k_eCitadelTeamObjective_Tier1' in instance.target:
            return {'target': 'Guardian', 'lane': lane,  'tier': tier}
        elif 'k_eCitadelTeamObjective_Tier2' in instance.target:
            return {'target': 'Walker', 'lane': lane}
        elif 'k_eCitadelTeamObjective_BarrackBoss' in instance.target:
            return {'target': 'Guardian', 'lane': lane, 'tier': 3}
        elif 'TitanShieldGenerator' in instance.target:
            return {'target': 'Shrine'}
        elif 'k_eCitadelTeamObjective_Titan' in instance.target:
            return {'target': 'Patron', 'tier': 1}
        elif 'k_eCitadelTeamObjective_Core' in instance.target:
            return {'target': 'Patron', 'tier': 2}
        else:
            return {'target': instance.target}



class MidbossEventSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()
    class Meta:
        model = MidbossEvent
        # fields = ['timestamp', 'type', 'team', 'details']
        fields = ['timestamp', 'type', 'details']

    def get_type(self, instance):
        return 'midboss'

    def get_details(self, instance):
        return {'target': instance.slayer}


class RejuvEventSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()

    class Meta:
        model = MidbossEvent
        # fields = ['timestamp', 'type', 'team', 'details']
        fields = ['timestamp', 'type', 'details']

    def get_type(self, instance):
        return 'rejuv'

    def get_details(self, instance):
        return {'target': instance.team}

