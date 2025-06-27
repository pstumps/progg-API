from rest_framework import serializers
from apps.matches.Models.MatchTimeline import MatchTimelineEvent, PvPEvent, ObjectiveEvent, MidbossEvent
import re


class MatchTimelineEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchTimelineEvent
        fields = '__all__'


class PvPEventSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()
    teamName = serializers.SerializerMethodField()

    class Meta:
        model = PvPEvent
        fields = ['teamName', 'type', 'timestamp', 'details']

    def get_teamName(self, instance):
        team = str(instance.team)
        if team == '0' or team == 'Team0':
            return 'Amber'
        elif team == '1' or team == 'Team1':
            return 'Sapphire'
        else:
            return team

    def get_type(self, instance):
        return 'pvp'

    def get_details(self, instance):
        return {'slayer': instance.slayer_hero_id, 'target': instance.victim_hero_id}


class ObjectiveEventSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()
    teamName = serializers.SerializerMethodField()

    class Meta:
        model = ObjectiveEvent
        fields = ['teamName', 'type', 'timestamp', 'details']

    def get_teamName(self, instance):
        team = str(instance.team).strip()
        if team == '0' or team == 'Team0':
            return 'Amber'
        elif team == '1' or team == 'Team1':
            return 'Sapphire'
        else:
            return team

    def get_type(self, instance):
        return 'obj'

    def get_details(self, instance):
        if instance.match.legacyFourLaneMap:
            obj_id_dict = {
                '1': {'target': 'Guardian', 'lane': 1, 'tier': 1},
                '2': {'target': 'Guardian', 'lane': 2, 'tier': 1},
                '3': {'target': 'Guardian', 'lane': 3, 'tier': 1},
                '4': {'target': 'Guardian', 'lane': 4, 'tier': 1},
                '5': {'target': 'Walker', 'lane': 1},
                '7': {'target': 'Walker', 'lane': 2},
                '8': {'target': 'Walker', 'lane': 3},
                '9': {'target': 'Walker', 'lane': 4},
                '10': {'target': 'Guardian', 'lane': 1, 'tier': 3},
                '11': {'target': 'Guardian', 'lane': 2, 'tier': 3},
                '12': {'target': 'Guardian', 'lane': 3, 'tier': 3},
                '13': {'target': 'Guardian', 'lane': 4, 'tier': 3},
                '14': {'target': 'Shrine'},
                '15': {'target': 'Shrine'},
                '0': {'target': 'Patron', 'tier': 2}
            }
        else:
            obj_id_dict = {
                '1': {'target': 'Guardian', 'lane': 1, 'tier': 1},
                '2': {'target': 'Guardian', 'lane': 2, 'tier': 1},
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
        if instance.target not in obj_id_dict:
            target_string = instance.target
            result = {}
            tier_pattern = re.match(r'Tier(\d)Lane(\d+)', target_string)
            if tier_pattern:
                tier = int(tier_pattern.group(1))
                lane = int(tier_pattern.group(2))
                result['target'] = 'Guardian' if tier == 1 else 'Walker'
                result['lane'] = lane
                result['tier'] = tier
                return result

            # Check for BarrackBossLaneX pattern
            barrack_pattern = re.match(r'BarrackBossLane(\d+)', target_string)
            if barrack_pattern:
                lane = int(barrack_pattern.group(1))
                result['target'] = 'Guardian'
                result['lane'] = lane
                return result

            # Check remaining specific targets
            if target_string == 'Titan':
                result['target'] = 'Titan'
                result['tier'] = 1
            elif target_string == 'TitanShieldGenerator':
                result['target'] = 'Shrine'
            elif target_string == 'Core':
                result['target'] = 'Patron'
                result['tier'] = 2


        return obj_id_dict.get(instance.target)

class MidbossEventSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    teamName = serializers.SerializerMethodField()

    class Meta:
        model = MidbossEvent
        fields = ['timestamp', 'type', 'teamName']


    def get_type(self, instance):
        return 'midboss'

    def get_teamName(self, instance):
        team = str(instance.slayer)
        if team == '0' or team == 'Team0':
            return 'Amber'
        elif team == '1' or team == 'Team1':
            return 'Sapphire'
        else:
            return team


class RejuvEventSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    teamName = serializers.SerializerMethodField()

    class Meta:
        model = MidbossEvent
        # fields = ['timestamp', 'type', 'team', 'details']
        fields = ['timestamp', 'type', 'teamName']

    def get_type(self, instance):
        return 'rejuv'

    def get_teamName(self, instance):
        team = str(instance.team)
        if team == '0' or team == 'Team0':
            return 'Amber'
        elif team == '1' or team == 'Team1':
            return 'Sapphire'
        else:
            return team
