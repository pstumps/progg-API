from rest_framework import serializers

from ..Models.PlayerHeroModel import PlayerHeroModel

class PlayerHeroModelSerializer(serializers.ModelSerializer):
    hero = serializers.SerializerMethodField()
    matches = serializers.IntegerField()
    wins = serializers.IntegerField()
    pickRate = serializers.SerializerMethodField()
    kills = serializers.IntegerField()
    deaths = serializers.IntegerField()
    assists = serializers.IntegerField()
    souls = serializers.IntegerField()
    soulsPerMin = serializers.FloatField()
    accuracy = serializers.FloatField()
    heroCritPercent = serializers.FloatField()
    heroDamage = serializers.IntegerField()
    objDamage = serializers.IntegerField()
    healing = serializers.IntegerField()
    lastHits = serializers.IntegerField()
    denies = serializers.IntegerField()
    multis = serializers.JSONField()
    streaks = serializers.JSONField()
    longestStreak = serializers.IntegerField()
    guardians = serializers.IntegerField()
    walkers = serializers.IntegerField()
    baseGuardians = serializers.IntegerField()
    shieldGenerators = serializers.IntegerField()
    patrons = serializers.IntegerField()
    midbosses = serializers.IntegerField()
    rejuvinators = serializers.IntegerField()
    tier = serializers.IntegerField()

    class Meta:
        model = PlayerHeroModel
        fields = ['hero', 'matches', 'wins', 'pickRate', 'kills', 'deaths', 'assists', 'souls', 'soulsPerMin',
                  'accuracy', 'heroCritPercent', 'heroDamage', 'objDamage', 'healing', 'lastHits', 'denies', 'multis',
                  'streaks', 'longestStreak', 'guardians', 'walkers', 'baseGuardians', 'shieldGenerators', 'patrons',
                  'midbosses', 'rejuvinators', 'tier']

    def get_hero(self, obj):
        return obj.hero.hero_deadlock_id


    def get_pickRate(self, obj):
        matches = obj.player.matches.count()
        return obj.matches / matches
