from rest_framework import serializers
from apps.matches.Models.MatchTimeline import MatchTimelineEvent, PvPEvent, ObjectiveEvent, MidbossEvent


class MatchTimelineEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchTimelineEvent
        fields = '__all__'


class PvPEventSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()
    team = serializers.SerializerMethodField()

    class Meta:
        model = PvPEvent
        fields = ['team', 'type', 'timestamp', 'details']

    def get_team(self, instance):
        if '0' in instance.team:
            return 'Amber'
        elif '1' in instance.team:
            return 'Sapphire'
        else:
            return instance.team

    def get_type(self, instance):
        return 'pvp'

    def get_details(self, instance):
        return {'slayer': instance.slayer_hero_id, 'target': instance.victim_hero_id}


class ObjectiveEventSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()
    team = serializers.SerializerMethodField()
    class Meta:
        model = ObjectiveEvent
        fields = ['type', 'timestamp', 'team', 'details']

    def get_team(self, instance):
        if '0' in instance.team:
            return 'Amber'
        elif '1' in instance.team:
            return 'Sapphire'
        else:
            return instance.team

    def get_type(self, instance):
        return 'obj'

    def get_details(self, instance):
        if instance.match.legacyFourLaneMap:
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
        else:
            obj_id_dict = {
                '1': {'target': 'Guardian', 'lane': 1, 'tier': 1},
                '3': {'target': 'Guardian', 'lane': 2, 'tier': 1},
                '4': {'target': 'Guardian', 'lane': 3, 'tier': 1},
                '5': {'target': 'Walker', 'lane': 1},
                '7': {'target': 'Walker', 'lane': 2},
                '8': {'target': 'Walker', 'lane': 3},
                '9': {'target': 'Guardian', 'lane': 1, 'tier': 3},
                '10': {'target': 'Guardian', 'lane': 2, 'tier': 3},
                '11': {'target': 'Guardian', 'lane': 3, 'tier': 3},
                '12': {'target': 'Shrine'},
                '14': {'target': 'Shrine'},
                '15': {'target': 'Patron', 'tier': 1},
                '0': {'target': 'Patron', 'tier': 2}
            }

            return obj_id_dict.get(instance.target)

class MidbossEventSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    team = serializers.SerializerMethodField()

    class Meta:
        model = MidbossEvent
        # fields = ['timestamp', 'type', 'team', 'details']
        fields = ['timestamp', 'type', 'team']


    def get_type(self, instance):
        return 'midboss'

    def get_team(self, instance):
        if '0' in instance.slayer:
            return 'Amber'
        elif '1' in instance.slayer:
            return 'Sapphire'
        else:
            return instance.slayer


class RejuvEventSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    team = serializers.SerializerMethodField()

    class Meta:
        model = MidbossEvent
        # fields = ['timestamp', 'type', 'team', 'details']
        fields = ['timestamp', 'type', 'team']

    def get_type(self, instance):
        return 'rejuv'

    def get_team(self, instance):
        if '0' in instance.team:
            return 'Amber'
        elif '1' in instance.team:
            return 'Sapphire'
        else:
            return instance.team

