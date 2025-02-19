from rest_framework.response import Response
from rest_framework.decorators import api_view
from .Models.MatchesModel import MatchesModel
from apps.players.Models.PlayerModel import PlayerModel
from apps.matches.services.MatchServices import MatchServices
from apps.matches.services.MetadataServices import MetadataServices
from proggbackend.services.DeadlockAPIData import deadlockAPIDataService
from proggbackend.services.DeadlockAPIAssets import deadlockAPIAssetsService
from .serializers.MatchModelSerializer import MatchModelSerailizer
from .serializers.UserMatchDetailsSerializer import UserMatchDetailsSerializer
from .serializers.scoreboard.MatchScoreboardSerializer import MatchScoreboardSerializer


@api_view(['GET'])
def match_details(request, dl_match_id):
    try:
        match = MatchesModel.objects.prefetch_related('matchPlayerModels', 'matchPlayerTimelineEvents').get(deadlock_id=dl_match_id)
    except MatchesModel.DoesNotExist:
        DataAPI = deadlockAPIDataService()
        matchMetadata = DataAPI.getMatchMetadata(dl_match_id)

        AssetsApi = deadlockAPIAssetsService()
        itemsDict = AssetsApi.getItemsDict()

        match = MetadataServices(itemsDict).createNewMatchFromMetadata(matchMetadata)

    matchServices = MatchServices()
    matchEvents  = matchServices.getMatchTimeline(match)
    print('Serializing match...')
    serializer = MatchScoreboardSerializer(match, context={'matchEvents': matchEvents})
    print('done!')
    return Response(serializer.data)

@api_view(['GET'])
def user_match_details(request, dl_match_id, user_id=None):
    try:
        match = MatchesModel.objects.prefetch_related('matchPlayerModels', 'matchPlayerTimelineEvents').get(deadlock_id=dl_match_id)
    except MatchesModel.DoesNotExist:
        return Response(status=404)

    '''
    if user_id is None and request.user.is_authenticated:
        user_id = request.user.id

    try:
        user = User.objects.get(id=user_id)
    except (User.DoesNotExist, PlayerModel.DoesNotExist):
        return Response(data={'details': 'User does not exist or does not have a player connected to their account.'}, status=404)
    if user_id:
        player = PlayerModel.objects.get(user=user)
        matchTimeline, playerTimeline = matchServices.getMatchTimeline(match, player)
        return Response({'matchTimeline': matchTimeline, 'playerTimeline': playerTimeline})
    '''

    matchServices = MatchServices()
    # Testing only
    player = PlayerModel.objects.get(steam_id3=44046862)
    matchPlayer = match.matchPlayerModels.get(player=player)
    playerTimeline, matchTimeline = matchServices.getMatchTimeline(match, matchPlayer)

    serializer = UserMatchDetailsSerializer(matchPlayer, context={'playerTimeline': playerTimeline})
    return Response(serializer.data)

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

@api_view(['GET'])
def create_match_from_metadata(request, dl_match_id):
    dlDataAPI = deadlockAPIDataService()
    dlAssetsAPI = deadlockAPIAssetsService()
    itemsDict = dlAssetsAPI.getItemsDict()

    MetadataService = MetadataServices(itemsDict)
    matchMetadata = dlDataAPI.getMatchMetadata(dl_match_id)
    if matchMetadata:
        match = MetadataService.createNewMatchFromMetadata(matchMetadata)
        serializer = MatchModelSerailizer(match)
        return Response(serializer.data)
        # return Response(stats=200)
    else:
        return Response(status=404)
