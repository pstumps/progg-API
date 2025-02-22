from rest_framework.response import Response
from rest_framework.decorators import api_view
from .Models.MatchesModel import MatchesModel
from apps.matches.Models.MatchPlayerModel import MatchPlayerModel
from apps.players.Models.PlayerModel import PlayerModel
from apps.matches.services.MatchServices import MatchServices
from .serializers.UserMatchDetailsSerializer import UserMatchDetailsSerializer
from .serializers.scoreboard.MatchScoreboardSerializer import MatchScoreboardSerializer


@api_view(['GET'])
def match_details(request, dl_match_id):
    matchServices = MatchServices()
    try:
        match = MatchesModel.objects.prefetch_related('matchPlayerModels', 'matchPlayerTimelineEvents').get(deadlock_id=dl_match_id)
    except MatchesModel.DoesNotExist:
        match = matchServices.createMatch(dl_match_id)
        if not match:
            return Response({'details': 'Match does not exist.'}, status=404)

    matchEvents  = matchServices.getMatchTimeline(match)
    print('Serializing match...')
    serializer = MatchScoreboardSerializer(match, context={'matchEvents': matchEvents})
    print('done!')
    return Response(serializer.data)

@api_view(['GET'])
def user_match_details(request, dl_match_id):
    try:
        match = MatchesModel.objects.prefetch_related('matchPlayerModels').get(deadlock_id=dl_match_id)
    except MatchesModel.DoesNotExist:
        return Response({'details': 'Match does not exist.'},status=404)

    matchPlayer = None
    user = request.user
    if user and user.playermodel:
        try:
            matchPlayer = match.matchPlayerModels.get(player=user.playermodel)
        except MatchPlayerModel.DoesNotExist:
            return Response({'details': 'User not in this match.'}, status=404)


    matchServices = MatchServices()
    print('Serializing match and player events...')
    playerEvents, matchEvents = matchServices.getMatchTimeline(match, matchPlayer)
    detailsSerializer = UserMatchDetailsSerializer(matchPlayer, context={'playerTimeline': playerEvents})
    print('done!')

    print('Serializing match...')
    scoreboardSerializer = MatchScoreboardSerializer(match, context={'matchEvents': matchEvents})
    print('done!')

    return Response({'userMatchDetails': detailsSerializer.data, 'matchScoreboardData': scoreboardSerializer.data})

@api_view(['GET'])
def timelines(request, dl_match_id, user_id=None):
    try:
        match = MatchesModel.objects.prefetch_related('matchPlayerModels', 'matchPlayerTimelineEvents').get(deadlock_id=dl_match_id)
    except MatchesModel.DoesNotExist:
        return Response(status=404)

    matchServices = MatchServices()

    # Testing only
    player = PlayerModel.objects.get(steam_id3=44046862)
    matchTimeline, playerTimeline = matchServices.getMatchTimeline(match, player)
    return Response({'matchTimeline': matchTimeline, 'playerTimeline': playerTimeline})
    # End Testing code

    #return Response({'matchTimeline': matchTimeline})
