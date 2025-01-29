from rest_framework import serializers
from apps.matches.Models import MatchPlayerModel


class MatchPlayerModelSerailizer(serializers.ModelSerializer):
    csSouls = serializers.IntegerField()
    kaSouls = serializers.IntegerField()
    otherSouls = serializers.IntegerField()
    avgHeroDmg = serializers.IntegerField()
    avgObjDmg = serializers.IntegerField()
    avgHealing = serializers.IntegerField()
    avgKills = serializers.IntegerField()
    avgAssists = serializers.IntegerField()
    avgDeaths = serializers.IntegerField()
    avgSouls = serializers.IntegerField()
    avgCS = serializers.IntegerField()
    avgSoulsPerMin = serializers.FloatField()


    class Meta:
        model = MatchPlayerModel
        fields = '__all__'


    def get_csSouls(self, obj):
        totalSouls = obj.soulsBreakdown
        csSouls = totalSouls.get('lane_creeps', 0) + totalSouls.get('neutrals', 0) + totalSouls.get('denies', 0)
        return csSouls

    def get_kaSouls(self, obj):
        totalSouls = obj.soulsBreakdown
        kaSouls = totalSouls.get('hero', 0) + totalSouls.get('assists', 0)
        return kaSouls

    def get_otherSouls(self, obj):
        totalSouls = obj.soulsBreakdown
        otherSouls = totalSouls.get('other', 0) + totalSouls.get('objectives', 0) + totalSouls.get('crates', 0)

        return otherSouls

    def get_avgHeroDmg(self, obj):
        total_hero_damage = obj.player.heroDamage
        total_matches = obj.player.matches.count()
        if total_matches > 0:
            return total_hero_damage / total_matches
        return 0

    def get_avgObjDmg(self, obj):
        total_obj_damage = obj.player.objDamage
        total_matches = obj.player.matches.count()
        if total_matches > 0:
            return total_obj_damage / total_matches
        return 0

    def get_avgHealing(self, obj):
        total_healing = obj.player.healing
        total_matches = obj.player.matches.count()
        if total_matches > 0:
            return total_healing / total_matches
        return 0

    def get_avgKills(self, obj):
        total_kills = obj.player.kills
        total_matches = obj.player.matches.count()
        if total_matches > 0:
            return total_kills / total_matches
        return 0

    def get_avgAssists(self, obj):
        total_assists = obj.player.assists
        total_matches = obj.player.matches.count()
        if total_matches > 0:
            return total_assists / total_matches
        return 0

    def get_avgDeaths(self, obj):
        total_deaths = obj.player.deaths
        total_matches = obj.player.matches.count()
        if total_matches > 0:
            return total_deaths / total_matches
        return 0

    def get_avgSouls(self, obj):
        total_souls = obj.player.souls
        total_matches = obj.player.matches.count()
        if total_matches > 0:
            return total_souls / total_matches
        return 0

    def get_avgCS(self, obj):
        total_cs = obj.player.lastHits
        total_matches = obj.player.matches.count()
        if total_matches > 0:
            return total_cs / total_matches
        return 0

    def get_avgSoulsPerMin(self, obj):
        return obj.player.soulsPerMin
