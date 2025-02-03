import time
from rest_framework.response import Response
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.throttling import UserRateThrottle
from .services import proGGPlayersService
from .throttles import StatsRateThrottle
from .serializers.PlayerModelSerializer import PlayerModelSerializer
from .serializers.PlayerHeroModelSerializer import PlayerHeroModelSerializer
from .serializers.PlayerMatchHistoryDataSerializer import MatchHistoryDataSerializer
from ..matches.serializers.MatchModelSerializer import MatchModelSerailizer
from .Models.PlayerModel import PlayerModel


def recentMatches(request, steam_id3):
    playersService = proGGPlayersService()
    lastTenMatches = playersService.getRecentMatches(steam_id3)

    # Check if player data is missing- a player has played a match but we don't have their metadata
    for recentMatch in lastTenMatches:
        if not recentMatch.abandoned:
            if recentMatch.accuracy == 0:
                playersService.fillInMissingMatchPlayerMetadata(recentMatch)

    return {'recentMatches': lastTenMatches}


@api_view(['GET'])
@throttle_classes([StatsRateThrottle])
def stats(request, steam_id3):
    # TODO Fix this

    playersService = proGGPlayersService()
    newPlayer = False
    try:
        print(f'Looking for player: {steam_id3}')
        player = PlayerModel.objects.get(steam_id3=steam_id3)
    except PlayerModel.DoesNotExist:
        # This is a new player. Create a player instance for them, and get their entire match history.
        print(f'Player does not exist. Creating new player for {steam_id3}')
        newPlayer = True

    if newPlayer:
        updated = playersService.updateMatchHistory(steam_id3)
        if not updated:
            return Response(
                data={"detail": "Player has no match history."},
                status=400
            )
        player = PlayerModel.objects.get(steam_id3=steam_id3)
        player.updatePlayerStats()
        # return Response(status=201, data={"detail": "New Player"})
    else:
        if (int(time.time()) - player.updated) / 60 > 900:
            if playersService.updateMatchHistory(steam_id3):
                player.updatePlayerStats()
    serializer = PlayerModelSerializer(player)
    return Response(status=200, data=serializer.data)


@api_view(['GET'])
def matchHistory(request, steam_id3):
    try:
        player = PlayerModel.objects.get(steam_id3=steam_id3)
    except PlayerModel.DoesNotExist:
        return Response(
            data={"detail": "Player not found."},
            status=404
        )
    history = player.matches
    serializer = MatchModelSerailizer(history, many=True)
    return Response(status=200, data=serializer.data)


@api_view(['GET'])
def topPlayerHeroes(request, steam_id3):
    playersService = proGGPlayersService()
    topHeroes = playersService.calculatePlayerHeroTiersForPlayerAndGetTopPlayerHeroes(steam_id3)
    serializer = PlayerHeroModelSerializer(topHeroes, many=True)
    return Response(status=200, data=serializer.data)


@api_view(['GET'])
def getMatchHistoryData(request, steam_id3):
    player = PlayerModel.objects.get(steam_id3=steam_id3)
    serializer = MatchHistoryDataSerializer(player)
    return Response(status=200, data=serializer.data)

@api_view(['GET'])
def deleteAllData(request):
    playersService = proGGPlayersService()
    playersService.deleteAllData()
    return Response({"detail": "All data deleted."})

