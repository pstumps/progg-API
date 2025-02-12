from rest_framework import serializers
from apps.matches.Models.MatchPlayerModel import MatchPlayerModel
from apps.heroes.Models.HeroesModel import HeroesModel
from apps.heroes.serializers import RecentMatchStatsHeroSerializer


class UserMatchDetailsSerializer(serializers.ModelSerializer):
    hero = serializers.SerializerMethodField()
    length = serializers.SerializerMethodField()
    team = serializers.SerializerMethodField()
    result = serializers.SerializerMethodField()
    csSouls = serializers.SerializerMethodField()
    kaSouls = serializers.SerializerMethodField()
    otherSouls = serializers.SerializerMethodField()
    avgHeroDmg = serializers.SerializerMethodField()
    avgObjDmg = serializers.SerializerMethodField()
    avgHealing = serializers.SerializerMethodField()
    avgKills = serializers.SerializerMethodField()
    avgAssists = serializers.SerializerMethodField()
    avgDeaths = serializers.SerializerMethodField()
    avgSouls = serializers.SerializerMethodField()
    avgCS = serializers.SerializerMethodField()
    avgSoulsPerMin = serializers.SerializerMethodField()
    records = serializers.SerializerMethodField()
    userMatchEvents = serializers.SerializerMethodField()

    class Meta:
        model = MatchPlayerModel
        fields = ['hero', 'length', 'team', 'result', 'kills', 'deaths', 'assists', 'lastHits', 'heroDamage',
                  'objDamage', 'healing', 'souls', 'csSouls', 'kaSouls', 'otherSouls', 'avgHeroDmg',
                  'avgObjDmg', 'avgHealing', 'avgKills', 'avgAssists', 'avgDeaths', 'avgSouls', 'avgCS',
                  'avgSoulsPerMin', 'records', 'userMatchEvents']

    def get_hero(self, obj):
        return RecentMatchStatsHeroSerializer(HeroesModel.objects.get(hero_deadlock_id=obj.hero_deadlock_id)).data

    def get_length(self, obj):
        return obj.match.length

    def get_team(self, obj):
        teamDict = {'k_ECitadelLobbyTeam_Team0': 'The Amber Hand', 'k_ECitadelLobbyTeam_Team1': 'The Sapphire Flame'}
        return teamDict[obj.team]

    def get_result(self, obj):
        if obj.match.victor == obj.team:
            return 'Victory'
        return 'Defeat'

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
        return total_hero_damage

    def get_avgObjDmg(self, obj):
        total_obj_damage = obj.player.objDamage
        total_matches = obj.player.matches.count()
        if total_matches > 0:
            return total_obj_damage / total_matches
        return total_obj_damage

    def get_avgHealing(self, obj):
        total_healing = obj.player.healing
        total_matches = obj.player.matches.count()
        if total_matches > 0:
            return total_healing / total_matches
        return total_healing

    def get_avgKills(self, obj):
        total_kills = obj.player.kills
        total_matches = obj.player.matches.count()
        if total_matches > 0:
            return total_kills / total_matches
        return total_kills

    def get_avgAssists(self, obj):
        total_assists = obj.player.assists
        total_matches = obj.player.matches.count()
        if total_matches > 0:
            return total_assists / total_matches
        return total_assists

    def get_avgDeaths(self, obj):
        total_deaths = obj.player.deaths
        total_matches = obj.player.matches.count()
        if total_matches > 0:
            return total_deaths / total_matches
        return total_deaths

    def get_avgSouls(self, obj):
        total_souls = obj.player.souls
        total_matches = obj.player.matches.count()
        if total_matches > 0:
            return total_souls / total_matches
        return total_souls

    def get_avgCS(self, obj):
        total_cs = obj.player.lastHits
        total_matches = obj.player.matches.count()
        if total_matches > 0:
            return total_cs / total_matches
        return total_cs

    def get_avgSoulsPerMin(self, obj):
        return obj.player.soulsPerMin

    def get_records(self, obj):
        arr = []
        records = obj.player.playerrecords_set.get().records
        for name, value in records.items():
            if name == 'kills' and value == [obj.hero_deadlock_id, obj.kills]:
                arr.append('kills')
            if name == 'deaths' and value == [obj.hero_deadlock_id, obj.deaths]:
                arr.append('deaths')
            if name == 'assists' and value == [obj.hero_deadlock_id, obj.assists]:
                arr.append('assists')
            if name == 'lastHits' and value == [obj.hero_deadlock_id, obj.lastHits]:
                arr.append('lastHits')
            if name == 'heroDamage' and value == [obj.hero_deadlock_id, obj.heroDamage]:
                arr.append('heroDamage')
            if name == 'objDamage' and value == [obj.hero_deadlock_id, obj.objDamage]:
                arr.append('objDamage')
            if name == 'healing' and value == [obj.hero_deadlock_id, obj.healing]:
                arr.append('healing')
        return arr

    def get_userMatchEvents(self, obj):
        return self.context['playerTimeline']