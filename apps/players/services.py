import time
from django.core.exceptions import ValidationError

from proggbackend.services.DeadlockAPIAnalytics import deadlockAPIAnalyticsService
from proggbackend.services.DeadlockAPIData import deadlockAPIDataService
from proggbackend.services.DeadlockAPIAssets import deadlockAPIAssetsService

from apps.matches.services.MetadataServices import MetadataServices
from ..matches.Models.MatchesModel import MatchesModel
from ..matches.services.MatchServices import MatchServices
from ..players.Models.PlayerModel import PlayerModel


class proGGPlayersService:
    def __init__(self):
        self.DLAPIAnalyticsService = deadlockAPIAnalyticsService()
        self.DLAPIDataService = deadlockAPIDataService()
        self.DLAPIAssetsService = deadlockAPIAssetsService()

    def calculatePlayerHeroTiersForPlayerAndGetTopPlayerHeroes(self, steam_id3):
        player = PlayerModel.objects.filter(steam_id3=steam_id3).first()
        if not player:
            return None

        player.calculatePlayerHeroTiers()
        return player.getTopPlayerHeroes()


    def updateMatchHistory(self, steam_id3, newPlayer=False):
        # Internal API Only
        if newPlayer:
            player = PlayerModel.objects.create(steam_id3=steam_id3)
            matchHistory = self.DLAPIAnalyticsService.getPlayerMatchHistory(account_id=steam_id3, has_metadata=True)
        else:
            try:
                player = PlayerModel.objects.prefetch_related('matches').get(steam_id3=steam_id3)
            except PlayerModel.DoesNotExist:
                print(f'Player {steam_id3} not found.')
                return False

            lastUpdateTime = None if not player.updated else player.updated
            matchHistory = self.DLAPIAnalyticsService.getPlayerMatchHistory(
                account_id=steam_id3,
                has_metadata=True,
                min_unix_timestamp=lastUpdateTime
            )

        # For testing only
        #matchHistory = [{'match_id': '32152804'}]
        if isinstance(matchHistory, dict) and matchHistory.get('detail'):
            print(f'No new matches since last update for player {steam_id3}')
            return True

        if not isinstance(matchHistory, list):
            print(f'Unexpected matchHistory response: {matchHistory}')
            return False

        if not matchHistory:
            print(f'Player {steam_id3} has no Match History.')
            return False

        DLItemsDict = self.DLAPIAssetsService.getItemsDict()
        metadataService = MetadataServices(DLItemsDict)
        matchesToAdd = []
        matchPlayersToAdd = []
        for i, match in enumerate(matchHistory, start=1):
            print(f'Processing match {i} of {len(matchHistory)}')
            if not isinstance(match, dict):
                print('Match is not a dictionary. Skipping...')
                continue

            matchId = match.get('match_id')
            if not matchId:
                print('match_id not found in Match History. Skipping...')
                continue

            if MatchesModel.objects.filter(deadlock_id=match['match_id']).exists():
                print(f"Match {match['match_id']} already exists.")
                if matchId not in {m.deadlock_id for m in player.matches.all()}:
                    print('Match not associated with player, adding match to player.')
                    oldMatch = MatchesModel.objects.prefetch_related('matchPlayerModels').get(deadlock_id=matchId)
                    matchesToAdd.append(oldMatch)

                    matchPlayers = oldMatch.matchPlayerModels.all()
                    playerMatchPlayers = player.matchPlayerModels.all()
                    for matchPlayer in matchPlayers:
                        if matchPlayer not in playerMatchPlayers:
                            matchPlayersToAdd.append(matchPlayer)
                continue

            matchMetadata = self.DLAPIDataService.getMatchMetadata(matchId)
            if not matchMetadata:
                print(f'Failed to get metadata for match {matchId}. Creating null match record.')
                nullMatch = MatchesModel.objects.create(
                    deadlock_id=matchId,
                    date=int(time.time())  # Current timestamp
                )
                matchesToAdd.append(nullMatch)
                continue
            metadataService.createNewMatchFromMetadata(matchMetadata)

        if matchesToAdd or matchPlayersToAdd:
            player.matches.add(*matchesToAdd)
            player.matchPlayerModels.add(*matchPlayersToAdd)
            player.save()

        return True

    def getOrCreateValidatedSteamPlayer(self, steam_id3):
        if PlayerModel.objects.filter(steam_id3=steam_id3).first():
            return PlayerModel.objects.filter(steam_id3=steam_id3).first()

        try:
            player = PlayerModel.objects.create(steam_id3=steam_id3)
            player.save()
            return player
        except ValidationError as e:
            print(f'e: {e}')
            print(f'Player not found in steam database.')
            return None

    def deleteAllData(self):
        matchService = MatchServices()
        matchService.deleteAllMatchesAndPlayersModels()

