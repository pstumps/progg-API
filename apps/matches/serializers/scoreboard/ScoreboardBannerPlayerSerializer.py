from rest_framework import serializers
from apps.matches.Models.MatchPlayerModel import MatchPlayerModel
from apps.heroes.Models.HeroesModel import HeroesModel
from apps.heroes.serializers import RecentMatchStatsHeroSerializer



class ScoreboardBannerPlayerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    hero = serializers.SerializerMethodField()
    rank = serializers.SerializerMethodField()
    lane = serializers.SerializerMethodField()
    build = serializers.SerializerMethodField()
    buildItems = serializers.SerializerMethodField()
    abilityOrder = serializers.SerializerMethodField()



    class Meta:
        model = MatchPlayerModel
        fields = ['steam_id3', 'name', 'hero', 'rank', 'lane', 'build', 'buildItems', 'kills', 'deaths', 'assists', 'souls', 'heroDamage',
                  'objDamage', 'healing', 'lastHits', 'soulsPerMin', 'level', 'accuracy', 'heroCritPercent', 'denies',
                  'abilityOrder', 'medals', 'soulsBreakdown', 'party']

    def get_name(self, obj):
        if obj.player:
            if obj.player.name == None:
                obj.player.updatePlayerFromSteamWebAPI()
                return obj.player.name
            return obj.player.name
        return None

    def get_hero(self, obj):
        hero = HeroesModel.objects.get(hero_deadlock_id=obj.hero_deadlock_id)
        return RecentMatchStatsHeroSerializer(hero).data

    def get_rank(self, obj):
        return None # TODO: Figure out how to get rank

    def get_lane(self, obj):
        return obj.lane

    def get_build(self, obj):
        build = {'weapon': 0, 'vitality': 0, 'spirit': 0,}
        percentArray = []

        for type, items in obj.items.items():
            if type != 'flex':
                build[type] = len(items)
            else:
                for fItem in items:
                    build[fItem['type']] += 1

        for count in build.values():
            filled = min(count, 8)
            percent = round(filled / 8 * 100, 2)
            percentArray.append(percent)

        return percentArray

    def get_buildItems(self, obj):
        buildItemsDict = {'orange': [], 'purple': [], 'green': [], 'flex': []}
        for type, items in obj.items.items():
            if type == 'weapon':
                buildItemsDict['orange'] = [i.replace(' ', '_') for i in items]
            elif type == 'spirit':
                buildItemsDict['purple'] = [i.replace(' ', '_') for i in items]
            elif type == 'vitality':
                buildItemsDict['green'] = [i.replace(' ', '_') for i in items]
            elif type == 'flex':
                for flexItem in items:
                    if flexItem['type'] == 'weapon':
                        flexItem['type'] = 'orange'
                    elif flexItem['type'] == 'spirit':
                        flexItem['type'] = 'purple'
                    elif flexItem['type'] == 'vitality':
                        flexItem['type'] = 'green'
                    flexItem['target'] = flexItem['target'].replace(' ', '_')
                    buildItemsDict['flex'].append({'type': flexItem['type'], 'target': flexItem['target']})
        return buildItemsDict

    def get_abilityOrder(self, obj):
        arr = []
        for ability in obj.abilities:
            arr.append({'name': ability[0].replace(' ', ''), 'level': len(ability[1])})
        return arr






