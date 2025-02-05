from rest_framework.response import Response
from rest_framework.decorators import api_view
from .Models.MatchesModel import MatchesModel
from .services import proggAPIMatchesService
from proggbackend.services.DeadlockAPIData import deadlockAPIDataService
from proggbackend.services.DeadlockAPIAssets import deadlockAPIAssetsService
from .serializers.MatchModelSerializer import MatchModelSerailizer
from .serializers.MatchCombinedTimelineSerializer import MatchCombinedTimelineSerializer

# Create your views here.

@api_view(['GET'])
def match_detail(request, dl_match_id):
    try:
        match = MatchesModel.objects.get(deadlock_id=dl_match_id)
    except MatchesModel.DoesNotExist:
        return Response(status=404)

    serializer = MatchModelSerailizer(match)
    return Response(serializer.data)

@api_view(['GET'])
def match_timeline(request, dl_match_id):
    try:
        match = MatchesModel.objects.get(deadlock_id=dl_match_id)
    except MatchesModel.DoesNotExist:
        return Response(status=404)

    matchTimelineSerializer = MatchCombinedTimelineSerializer(match)
    timeline = matchTimelineSerializer.data

    return Response(timeline)

@api_view(['GET'])
def create_match_from_metadata(request, dl_match_id):
    dlDataAPI = deadlockAPIDataService()
    dlAssetsAPI = deadlockAPIAssetsService()
    itemsDict = dlAssetsAPI.getItemsDict()

    proggMatchService = proggAPIMatchesService(itemsDict)
    matchMetadata = dlDataAPI.getMatchMetadata(dl_match_id)
    if matchMetadata:
        match = proggMatchService.createNewMatchFromMetadata(matchMetadata)
        serializer = MatchModelSerailizer(match)
        return Response(serializer.data)
        # return Response(stats=200)
    else:
        return Response(status=404)


