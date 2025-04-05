import time
from rest_framework.response import Response
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.throttling import UserRateThrottle

from .serializers.PlayerRecordsSerializer import PlayerRecordsSerializer
from .services import PlayersServices
from proggbackend.services.SteamWebAPI import SteamWebAPIService
from proggbackend.services.DeadlockAPIAssets import deadlockAPIAssetsService
from proggbackend.services.DeadlockAPIAnalytics import deadlockAPIAnalyticsService
from .serializers.PlayerModelSerializer import PlayerModelSerializer
from .serializers.PlayerHeroModelSerializer import PlayerHeroModelSerializer
from .serializers.PlayerMatchHistoryDataSerializer import MatchHistoryDataSerializer
from .serializers.SearchHistoryPlayerSerializer import SearchHistoryPlayer
from ..matches.serializers.RecentMatchPlayerModelSerializer import RecentMatchPlayerModelSerializer
from .Models.PlayerModel import PlayerModel
from .Models.PlayerRecords import PlayerRecords


@api_view(['GET'])
#@throttle_classes([StatsRateThrottle])
def stats(request, steam_id3):
    playersService = PlayersServices()
    newPlayer = False
    try:
        print(f'Looking for player: {steam_id3}')
        player = PlayerModel.objects.get(steam_id3=steam_id3)
    except PlayerModel.DoesNotExist:
        # This is a new player. Create a player instance for them, and get their entire match history.
        print(f'Player does not exist. Creating new player for {steam_id3}')
        newPlayer = True

    # Testing only
    if newPlayer:
        #TODO: Use celery to update player match history
        updated = playersService.updateMatchHistory(steam_id3, newPlayer)
        if not updated:
            return Response(
                data={"detail": "Player has no match history."},
                status=400
            )
        player = PlayerModel.objects.get(steam_id3=steam_id3)
        player.updatePlayerFromSteamWebAPI()
        player.updatePlayerStats()
        player.save()
        # return Response(status=201, data={"detail": "New Player"})
    else:
        if player:
            print('Player exists.')
            if (int(time.time()) - (player.updated or 0)) > (60 * 15):
                print('Updating player...')
                if playersService.updateMatchHistory(steam_id3):
                    player.updatePlayerFromSteamWebAPI()
                    player.updatePlayerStats()
                else:
                    return Response(
                        data={"detail": "Player does not exist or has no match history."},
                        status=400
                    )
    serializer = PlayerModelSerializer(player)
    return Response(status=200, data=serializer.data)

@api_view(['GET'])
#@throttle_classes([StatsRateThrottle])
def testStats(request, steam_id3):
    playersService = PlayersServices()
    newPlayer = False
    try:
        print(f'Looking for player: {steam_id3}')
        player = PlayerModel.objects.get(steam_id3=steam_id3)
    except PlayerModel.DoesNotExist:
        # This is a new player. Create a player instance for them, and get their entire match history.
        print(f'Player does not exist. Creating new player for {steam_id3}')
        newPlayer = True

    # Testing only
    if newPlayer:
        #TODO: Use celery to update player match history
        player = PlayerModel.objects.get(steam_id3=steam_id3)
        player.updated = int(time.time())
        player.save()
        # return Response(status=201, data={"detail": "New Player"})
    else:
        if player:
            print('Player exists.')
            if (int(time.time()) - (player.updated or 0)) > (60 * 15):
                print('Updating player...')
                player.updatePlayerStats()

    serializer = PlayerModelSerializer(player)
    return Response(status=200, data=serializer.data)

@api_view(['GET'])
def playerHeroes(request, steam_id3):
    try:
        player = PlayerModel.objects.get(steam_id3=steam_id3)
    except PlayerModel.DoesNotExist:
        return Response(
            data={'detail': 'Player not found.'},
            status=404
        )

    playerHeroes = player.player_hero_stats.all()
    pheroSerializer = PlayerHeroModelSerializer(playerHeroes, many=True)

    return Response(data=pheroSerializer.data, status=200)


@api_view(['GET'])
def matchHistory(request, steam_id3):
    try:
        player = PlayerModel.objects.get(steam_id3=steam_id3)
    except PlayerModel.DoesNotExist:
        return Response(
            data={"detail": "Player not found."},
            status=404
        )
    history = player.matchPlayerModels.all().order_by('-match__date')
    serializer = RecentMatchPlayerModelSerializer(history, many=True)
    return Response(status=200, data=serializer.data)


@api_view(['GET'])
def topPlayerHeroes(request, steam_id3):
    playersService = PlayersServices()
    topHeroes = playersService.calculatePlayerHeroTiersForPlayerAndGetTopPlayerHeroes(steam_id3)
    serializer = PlayerHeroModelSerializer(topHeroes, many=True)
    return Response(status=200, data=serializer.data)


@api_view(['GET'])
def getMatchHistoryData(request, steam_id3):
    player = PlayerModel.objects.get(steam_id3=steam_id3)
    serializer = MatchHistoryDataSerializer(player)
    return Response(status=200, data=serializer.data)

@api_view(['GET'])
def getSteamInfo(request, steam_id3):
    steamService = SteamWebAPIService()
    playerInfo = steamService.getPlayerSummaries(steam_id3)
    return Response(status=200, data=playerInfo)

@api_view(['GET'])
def updatePlayerSteamWebAPI(request, steam_id3):
    player = PlayerModel.objects.get(steam_id3=steam_id3)
    player.updatePlayerFromSteamWebAPI()
    player.save()
    return Response(status=200, data={"detail": "Player updated."})


@api_view(['GET'])
def deleteAllData(request):
    playersService = PlayersServices()
    playersService.deleteAllData()
    return Response({"detail": "All data deleted."})

@api_view(['GET'])
def getDeadlockAPIMatchHistory(request, steam_id3):
    playersService = deadlockAPIAnalyticsService()
    history = playersService.getPlayerMatchHistory(steam_id3)
    return Response({"detail": history})

@api_view(['GET'])
def search_history_player_item(request, steam_id3):
    try:
        player = PlayerModel.objects.get(steam_id3=steam_id3)
    except PlayerModel.DoesNotExist:
        return Response(status=404)
    serializer = SearchHistoryPlayer(player)
    return Response(status=200, data=serializer.data)

@api_view(['GET'])
def playerRecords(request, steam_id3):
    try:
        player = PlayerModel.objects.get(steam_id3=steam_id3)
    except PlayerModel.DoesNotExist:
        return Response(status=404)
    try:
        player_records = player.playerrecords_set.get()
    except PlayerRecords.DoesNotExist:
        return Response(status=404)

    print(player_records)

    serializer = PlayerRecordsSerializer(player_records)
    return Response(status=200, data=serializer.data)

@api_view(['GET'])
def calculateRank(request, steam_id3):
    try:
        player = PlayerModel.objects.get(steam_id3=steam_id3)
    except PlayerModel.DoesNotExist:
        return Response(status=404)

    player.calculateRank()
    return Response(status=200, data=player.rank)

