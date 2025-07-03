from apps.heroes.Models.HeroesModel import HeroesModel
from apps.matches.Models.MatchesModel import MatchesModel
from apps.matches.Models.MatchPlayerModel import MatchPlayerModel
from apps.matches.Models.MatchPlayerTimeline import MatchPlayerTimelineEvent
from apps.players.Models.PlayerModel import PlayerModel
from apps.players.Models.PlayerHeroModel import PlayerHeroModel
from apps.players.Models.PlayerRecords import PlayerRecords
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
                         '1': 'Sapphire',
                         'Team0': 'Amber',
                         'Team1': 'Sapphire'}


    def createMatch(self, dl_match_id):
        DataAPI = deadlockAPIDataService()
        matchMetadata = DataAPI.getMatchMetadata(dl_match_id)
        AssetsApi = deadlockAPIAssetsService()
        itemsDict = AssetsApi.getItemsDict()
        matchServices = MetadataServices(DLItemsDict=itemsDict)
        match = matchServices.createNewMatchFromMetadata(matchMetadata)
        match.save()
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
                    serializedEvents.append(objEvent)
            else:
                continue

        return serializedEvents

    def serializeMidbossEvents(self, midbossEvents):
        serializedEvents = []
        for event in midbossEvents:
            if isinstance(event, MidbossEvent):
                if event.team:
                    midbossEvent = MidbossEventSerializer(event).data
                    rejuvEvent = RejuvEventSerializer(event).data
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

    def getPlayersInMatchFromMatchMetadata(self, matchMetadata):
        players = []
        match_info = matchMetadata.get('match_info')
        if not match_info:
            return players
        for player in match_info.get('players'):
            players.append(player.get('account_id'))
        return players

    def crawlMatches(self, initial_match_id):
        visited = set()
        total_processed = self.crawlMatchesAndPlayers(initial_match_id, visited)
        return total_processed

    def crawlMatchesAndPlayers(self, deadlock_id, visited=None):
        from django.core.cache import cache
        from apps.players.services import PlayersServices

        if not deadlock_id:
            return 0

        if cache.get('crawl_stop_signal', False):
            print("Crawl stopped by user.")
            return 0

        if visited is None:
            visited = set()
        if deadlock_id in visited:
            return 0

        visited.add(deadlock_id)

        already_processed = MatchesModel.objects.filter(deadlock_id=deadlock_id, processed=True).exists()
        if already_processed:
            print(f'Match {deadlock_id} already processed, skipping.')
            return 0

        # Retrieve metadata
        dataService = deadlockAPIDataService()
        matchMetadata = dataService.getMatchMetadata(dl_match_id=deadlock_id)
        if not matchMetadata:
            print(f"No metadata for match {deadlock_id}, skipping.")
            return 0

        playersInMatch = self.getPlayersInMatchFromMatchMetadata(matchMetadata)

        playerService = PlayersServices()
        new_matches = []
        for playerId in playersInMatch:
            player = PlayerModel.objects.filter(steam_id3=playerId).first()
            if player is None:
                matchesProcessed = playerService.updateMatchHistoryForCrawl(playerId, newPlayer=True)
            else:
                matchesProcessed = playerService.updateMatchHistoryForCrawl(playerId)

            if matchesProcessed and isinstance(matchesProcessed, list):
                new_matches.extend(matchesProcessed)


        processed_count = 1

        #current_count = cache.get('matches_crawled', 0)
        #cache.set('matches_crawled', current_count + 1)
        cache.incr('matches_crawled')

        print(f"Processed match {deadlock_id}. New matches discovered: {len(new_matches)}")

        MatchesModel.objects.filter(deadlock_id=deadlock_id).update(processed=True)

        # Recursively process each newly discovered match
        for m in new_matches:
            if cache.get('crawl_stop_signal', False):
                print("Crawl stopped manually.")
                break

            if not m or not getattr(m, 'deadlock_id', None):
                continue
            next_id = m.deadlock_id
            if next_id not in visited:
                processed_count += self.crawlMatchesAndPlayers(next_id, visited)


        print(f"Done exhausting matches discovered from {deadlock_id}. "
              f"Total processed in this chain: {processed_count}")

        return processed_count


    def deleteAllMatchesAndPlayersModels(self):
        MatchesModel.objects.all().delete()
        MatchPlayerModel.objects.all().delete()
        MatchPlayerTimelineEvent.objects.all().delete()
        PlayerModel.objects.all().delete()
        PlayerHeroModel.objects.all().delete()
        PlayerRecords.objects.all().delete()
        PvPEvent.objects.all().delete()
        ObjectiveEvent.objects.all().delete()
        MidbossEvent.objects.all().delete()
