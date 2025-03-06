from apps.heroes.Models.HeroesModel import HeroesModel
from apps.matches.Models.MatchesModel import MatchesModel
from apps.matches.Models.MatchPlayerModel import MatchPlayerModel
from apps.matches.Models.MatchPlayerTimeline import MatchPlayerTimelineEvent
from apps.players.Models.PlayerModel import PlayerModel
from apps.players.Models.PlayerHeroModel import PlayerHeroModel
from apps.matches.Models.MatchTimeline import PvPEvent, ObjectiveEvent, MidbossEvent
from apps.matches.serializers.event.MatchTimelineEventSerializer import PvPEventSerializer, ObjectiveEventSerializer, MidbossEventSerializer, RejuvEventSerializer
from apps.matches.serializers.event.MatchPlayerTimelineEventSerializer import AbilityEventSerializer, BuyEventSerializer, SellEventSerializer


from apps.matches.services.MetadataServices import MetadataServices
from proggbackend.services.DeadlockAPIData import deadlockAPIDataService
from proggbackend.services.DeadlockAPIAssets import deadlockAPIAssetsService


class MatchServices:
    def __init__(self):
        self.teamDict = {'k_ECitadelLobbyTeam_Team0': 'Amber',
                         'k_ECitadelLobbyTeam_Team1': 'Sapphire',
                         '0': 'Amber',
                         '1': 'Sapphire'}


    def createMatch(self, dl_match_id):
        DataAPI = deadlockAPIDataService()
        matchMetadata = DataAPI.getMatchMetadata(dl_match_id)
        AssetsApi = deadlockAPIAssetsService()
        itemsDict = AssetsApi.getItemsDict()
        match = MetadataServices(itemsDict).createNewMatchFromMetadata(matchMetadata)
        return match


    def getMatchTimeline(self, match, matchPlayer=None):
        all_heroes = HeroesModel.objects.all()
        pvpEvents = list(match.pvpevent.all())
        pvpSerialized = self.serializePvpEvents(pvpEvents, all_heroes)
        objectiveEvents = list(match.objectiveevent.all())
        objectiveSerialized = self.serializeObjectiveEvents(objectiveEvents)
        midbossEvents = list(match.midbossevent.all())
        midbossSerialized = self.serializeMidbossEvents(midbossEvents)

        matchTimeline = sorted(pvpSerialized + objectiveSerialized + midbossSerialized, key=lambda x: x['timestamp'])

        if matchPlayer:
            matchPlayerEvents = match.matchPlayerTimelineEvents.filter(player=matchPlayer.player)
            playerSerialized = self.serializePlayerEvents(matchPlayerEvents)

            player_pvpSerialized = [
                event for event in pvpSerialized
                if event['details']['target'] == all_heroes.get(
                    hero_deadlock_id=matchPlayer.hero_deadlock_id).name.lower() or event['details']['slayer'] == all_heroes.get(hero_deadlock_id=matchPlayer.hero_deadlock_id).name.lower()
            ]

            playerTimeline = sorted(player_pvpSerialized + playerSerialized + objectiveSerialized + midbossSerialized,
                                    key=lambda x: x['timestamp'])

            return playerTimeline, matchTimeline
        return matchTimeline

    def serializePvpEvents(self, pvpEvents, all_heroes):
        serializedEvents = []
        for event in pvpEvents:
            if isinstance(event, PvPEvent):
                pvpEvent = PvPEventSerializer(event).data
                pvpEvent['details']['slayer'] = all_heroes.get(hero_deadlock_id=event.slayer_hero_id).name.lower()
                pvpEvent['details']['target'] = all_heroes.get(hero_deadlock_id=event.victim_hero_id).name.lower()
                serializedEvents.append(pvpEvent)
            else:
                continue

        return serializedEvents

    def serializeObjectiveEvents(self, objectiveEvents):
        serializedEvents = []
        for event in objectiveEvents:
            if isinstance(event, ObjectiveEvent):
                if event.timestamp == 0:
                    continue
                else:
                    objEvent = ObjectiveEventSerializer(event).data
                    objEvent['team'] = self.teamDict.get(event.team)
                    serializedEvents.append(objEvent)
            else:
                continue

        return serializedEvents

    def serializeMidbossEvents(self, midbossEvents):
        serializedEvents = []
        for event in midbossEvents:
            if isinstance(event, MidbossEvent):
                if event.slayer:
                    midbossEvent = MidbossEventSerializer(event).data
                    midbossEvent['details']['target'] = self.teamDict.get(event.slayer)
                    rejuvEvent = RejuvEventSerializer(event).data
                    rejuvEvent['details']['target'] = self.teamDict.get(event.team)
                    serializedEvents.extend([midbossEvent, rejuvEvent])
                else:
                    midbossEvent = MidbossEventSerializer(event).data
                    serializedEvents.append(midbossEvent)
            else:
                continue

        return serializedEvents

    def serializePlayerEvents(self, matchPlayerEvents):
        serializedEvents = []
        for event in matchPlayerEvents:
            if isinstance(event, MatchPlayerTimelineEvent):
                if event.type == 'level':
                    levelEvent = AbilityEventSerializer(event).data
                    serializedEvents.append(levelEvent)
                elif event.type == 'item':
                    if event.details.get('sold_time_s'):
                        buyEvent = BuyEventSerializer(event).data
                        sellEvent = SellEventSerializer(event).data
                        serializedEvents.extend([buyEvent, sellEvent])
                    else:
                        serializer = BuyEventSerializer(event)
                        event_data = serializer.data
                        serializedEvents.append(event_data)
            else:
                continue

        return serializedEvents


    def deleteAllMatchesAndPlayersModels(self):
        MatchesModel.objects.all().delete()
        MatchPlayerModel.objects.all().delete()
        MatchPlayerTimelineEvent.objects.all().delete()
        PlayerModel.objects.all().delete()
        PlayerHeroModel.objects.all().delete()
        PvPEvent.objects.all().delete()
        ObjectiveEvent.objects.all().delete()
        MidbossEvent.objects.all().delete()
