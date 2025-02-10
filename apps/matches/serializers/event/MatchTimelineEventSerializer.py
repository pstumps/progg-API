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
        if 'Tier1' in instance.target:
            return {'target': 'Guardian'}
        elif 'Tier2' in instance.target:
            return {'target': 'Walker'}
        elif 'BarrackBoss' in instance.target:
            return {'target': 'BaseGuardian'}
        elif 'TitanShieldGenerator' in instance.target:
            return {'target': 'Shrine'}
        elif 'k_eCitadelTeamObjective_Core' in instance.target:
            return {'target': 'Patron'}


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

