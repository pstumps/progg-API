from rest_framework.response import Response
from rest_framework.decorators import api_view
from .Models.MatchesModel import MatchesModel
from apps.matches.Models.MatchPlayerModel import MatchPlayerModel
from apps.players.Models.PlayerModel import PlayerModel
from apps.matches.services.MatchServices import MatchServices
from apps.matches.services.MetadataServices import MetadataServices
from .serializers.UserMatchDetailsSerializer import UserMatchDetailsSerializer
from .serializers.scoreboard.MatchScoreboardSerializer import MatchScoreboardSerializer
from .serializers.MatchHistoryItemSerializer import MatchHistoryItemSerializer
from proggbackend.services.DeadlockAPIData import deadlockAPIDataService
from proggbackend.services.DeadlockAPIAssets import deadlockAPIAssetsService


@api_view(['GET'])
def match_details(request, dl_match_id):
    matchServices = MatchServices()
    try:
        match = MatchesModel.objects.prefetch_related('matchPlayerModels', 'matchPlayerTimelineEvents').get(deadlock_id=dl_match_id)

    except MatchesModel.DoesNotExist:
        match = matchServices.createMatch(dl_match_id)
        if not match:
            return Response({'details': 'Match does not exist.'}, status=404)

    matchPlayer = None
    playerEvents = None
    user = request.user
    if user.is_authenticated and hasattr(user, 'playermodel'):
        try:
            matchPlayer = match.matchPlayerModels.get(player=user.playermodel)
            playerEvents, matchEvents = matchServices.getMatchTimeline(match, matchPlayer)
        except MatchPlayerModel.DoesNotExist:
            print('User not in match')
            matchEvents = matchServices.getMatchTimeline(match)
    else:
        matchEvents = matchServices.getMatchTimeline(match)


    dlAPIDataService = deadlockAPIDataService()
    metadata = dlAPIDataService.getMatchMetadata(dl_match_id)

    print('Constructing graphs...')
    AssetsApi = deadlockAPIAssetsService()
    itemsDict = AssetsApi.getItemsDictIndexedByClassname()
    metadataService = MetadataServices(itemsDict)
    graphData = metadataService.getPlayerGraphs(metadata)
    damageGraphData = metadataService.getPlayerDamageGraphs(metadata)
    print('done!')

    print('Serializing match...')
    serializer = MatchScoreboardSerializer(match, context={'matchEvents': matchEvents,
                                                           'graphData': graphData,
                                                           'damageGraphData': damageGraphData})
    print('done!')

    response_data = {'matchScoreboardData': serializer.data}

    if matchPlayer and playerEvents:
        print('Serializing user...')
        detailsSerializer = UserMatchDetailsSerializer(matchPlayer, context={'playerTimeline': playerEvents})
        print('done!')
        response_data['userMatchDetails'] = detailsSerializer.data
    else:
        response_data['userMatchDetails'] = None

    return Response(response_data)

@api_view(['GET'])
def match_details_test(request, dl_match_id):
    matchServices = MatchServices()
    try:
        match = MatchesModel.objects.prefetch_related('matchPlayerModels', 'matchPlayerTimelineEvents').get(deadlock_id=dl_match_id)

    except MatchesModel.DoesNotExist:
        match = matchServices.createTestMatch(dl_match_id)
        if not match:
            return Response({'details': 'Match does not exist.'}, status=404)

    matchPlayer = None
    playerEvents = None
    user = request.user
    if user.is_authenticated and hasattr(user, 'playermodel'):
        try:
            matchPlayer = match.matchPlayerModels.get(player=user.playermodel)
            playerEvents, matchEvents = matchServices.getMatchTimeline(match, matchPlayer)
        except MatchPlayerModel.DoesNotExist:
            print('User not in match')
            matchEvents = matchServices.getMatchTimeline(match)
    else:
        matchEvents = matchServices.getMatchTimeline(match)


    dlAPIDataService = deadlockAPIDataService()
    metadata = dlAPIDataService.getMatchMetadataTest(dl_match_id)

    print('Constructing graphs...')
    AssetsApi = deadlockAPIAssetsService()
    itemsDict = AssetsApi.getItemsDictIndexedByClassname()
    metadataService = MetadataServices(itemsDict)
    graphData = metadataService.getPlayerGraphs(metadata)
    damageGraphData = metadataService.getPlayerDamageGraphs(metadata)
    print('done!')

    print('Serializing match...')
    serializer = MatchScoreboardSerializer(match, context={'matchEvents': matchEvents,
                                                           'graphData': graphData,
                                                           'damageGraphData': damageGraphData})
    print('done!')

    response_data = {'matchScoreboardData': serializer.data}

    if matchPlayer and playerEvents:
        print('Serializing user...')
        detailsSerializer = UserMatchDetailsSerializer(matchPlayer, context={'playerTimeline': playerEvents})
        print('done!')
        response_data['userMatchDetails'] = detailsSerializer.data
    else:
        response_data['userMatchDetails'] = None

    return Response(response_data)

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
    dlAPIDataService = deadlockAPIDataService()


    matchServices = MatchServices()
    print('Serializing events...')
    playerEvents, matchEvents = matchServices.getMatchTimeline(match, matchPlayer)
    detailsSerializer = UserMatchDetailsSerializer(matchPlayer, context={'playerTimeline': playerEvents})
    print('done!')

    metadata = dlAPIDataService.getMatchMetadata(dl_match_id)
    metadataServices = MetadataServices()
    graphData = metadataServices.getPlayerGraphs(metadata)
    print('Serializing match...')
    scoreboardSerializer = MatchScoreboardSerializer(match, context={'matchEvents': matchEvents, 'graphData': graphData})
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

@api_view(['GET'])
def graphs(request, dl_match_id):
    dlAPIDataService = deadlockAPIDataService()
    metadata = dlAPIDataService.getMatchMetadata(dl_match_id)

    metadataService = MetadataServices()
    graphs = metadataService.getPlayerGraphs(metadata)

    return Response(data=graphs, status=200)


@api_view(['GET'])
def damageGraphs(request, dl_match_id):
    AssetsApi = deadlockAPIAssetsService()
    itemsDict = AssetsApi.getItemsDictIndexedByClassname()
    metadataService = MetadataServices(itemsDict)
    dmgGraphs = metadataService.getPlayerDamageGraphs(dl_match_id)

    return Response(data=dmgGraphs, status=200)

@api_view(['GET'])
def search_history_match_item(request, dl_match_id):
    try:
        match = MatchesModel.objects.get(deadlock_id=dl_match_id)
    except MatchesModel.DoesNotExist:
        return Response(status=404)

    serializer = MatchHistoryItemSerializer(match)
    return Response(serializer.data)


@api_view(['GET'])
def crawl_matches(request, dl_match_id):
    from django.core.cache import cache

    cache.set('crawl_stop_signal', False)
    cache.set('matches_crawled', 0)

    matchServices = MatchServices()
    count = matchServices.crawlMatches(dl_match_id)

    cache.delete('crawl_stop_signal')
    cache.delete('matches_crawled')

    return Response({'details': str(count) + ' matches crawled.'})

@api_view(['GET'])
def stop_crawl(request):
    from django.core.cache import cache

    cache.set('crawl_stop_signal', True)
    matches_counted = cache.get('matches_crawled', 0)

    return Response({'details': f'Crawl stopping. {matches_counted} matches processed so far.'})

@api_view(['GET'])
def crawl_status(request):
    from django.core.cache import cache

    is_stopping = cache.get('crawl_stop_signal', False)
    matches_counted = cache.get('matches_crawled', 0)
    status = 'stopping' if is_stopping else 'running'

    return Response({
        'status': status,
        'matches_processed': matches_counted
    })