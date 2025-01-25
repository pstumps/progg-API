from rest_framework.response import Response
from rest_framework.decorators import api_view
from .services import proGGPlayersService
from .serializers import PlayerModelSerializer, PlayerHeroModelSerializer
from .Models.PlayerHeroModel import PlayerHeroModel
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
    try:
        player = PlayerModel.objects.get(steam_id3=steam_id3)
        playerHeroes = PlayerHeroModel.objects.filter(player=player)
        print(playerHeroes)
        player.updatePlayerStats()
    except PlayerModel.DoesNotExist:
        return Response(status=404)

    serializer = PlayerModelSerializer(player)
    return Response(serializer.data)

