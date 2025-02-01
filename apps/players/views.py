import traceback
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .services import proGGPlayersService
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
def stats(request, steam_id3):
    playersService = proGGPlayersService()
    try:
        player = PlayerModel.objects.get(steam_id3=steam_id3)
        playersService.getMatchHistory(steam_id3)
        player.updatePlayerStats()
    except PlayerModel.DoesNotExist:
        # TODO: change how case where no data on this player exists is handled

        matches = playersService.getMatchHistory(steam_id3)
        if not matches:
            return Response(status=400)


    player = PlayerModel.objects.get(steam_id3=steam_id3)

    serializer = PlayerModelSerializer(player)
    return Response(serializer.data)


@api_view(['GET'])
def matchHistory(request, steam_id3):
    playersService = proGGPlayersService()
    history = playersService.getMatchHistory(steam_id3)
    serializer = MatchModelSerailizer(history, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def topPlayerHeroes(request, steam_id3):
    playersService = proGGPlayersService()
    topHeroes = playersService.calculatePlayerHeroTiersForPlayerAndGetTopPlayerHeroes(steam_id3)
    serializer = PlayerHeroModelSerializer(topHeroes, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def getMatchHistoryData(request, steam_id3):
    player = PlayerModel.objects.get(steam_id3=steam_id3)
    serializer = MatchHistoryDataSerializer(player)
    return Response(serializer.data)

