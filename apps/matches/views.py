from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.auth.models import User
from .Models.MatchesModel import MatchesModel
from apps.players.Models.PlayerModel import PlayerModel
from .services import proggAPIMatchesService
from proggbackend.services.DeadlockAPIData import deadlockAPIDataService
from proggbackend.services.DeadlockAPIAssets import deadlockAPIAssetsService
from .serializers.MatchModelSerializer import MatchModelSerailizer
from apps.matches.Models.MatchTimeline import PvPEvent, ObjectiveEvent, MidbossEvent
from apps.matches.Models.MatchPlayerTimeline import MatchPlayerTimelineEvent
from apps.matches.serializers.event.MatchTimelineEventSerializer import MatchTimelineEventSerializer, PvPEventSerializer, ObjectiveEventSerializer, MidbossEventSerializer, RejuvEventSerializer
from apps.matches.serializers.event.MatchPlayerTimelineEventSerializer import AbilityEventSerializer, BuyEventSerializer, SellEventSerializer


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
def timelines(request, dl_match_id, user_id=None):
    try:
        match = MatchesModel.objects.prefetch_related('matchPlayerModels', 'matchPlayerTimelineEvents').get(deadlock_id=dl_match_id)
    except MatchesModel.DoesNotExist:
        return Response(status=404)

    '''
    if user_id is None and request.user.is_authenticated:
        user_id = request.user.id

    try:
        user = User.objects.get(id=user_id)
        player = PlayerModel.objects.get(user=user)
        matchPlayer = match.matchPlayerModels.filter(player=player).first()
    except (User.DoesNotExist, PlayerModel.DoesNotExist):
        return Response(data={'details': 'User does not exist or does not have a player connected to their account.'}, status=404)
    '''

    # Testing only
    player = PlayerModel.objects.get(steam_id3=55025907)
    matchPlayer = match.matchPlayerModels.filter(player=player).first()
    # End Testing code

    pvpEvents = list(match.pvpevent.all())
    objectiveEvents = list(match.objectiveevent.all())
    midbossEvents = list(match.midbossevent.all())
    timelineEvents = pvpEvents + objectiveEvents + midbossEvents

    pvpSerialized = []
    objectiveSerialized = []
    midbossSerialized = []
    for event in timelineEvents:
        if isinstance(event, PvPEvent):
            pvpEvent = PvPEventSerializer(event).data
            pvpSerialized.append(pvpEvent)
        elif isinstance(event, ObjectiveEvent):
            if event.timestamp == 0:
                continue
            else:
                objEvent = ObjectiveEventSerializer(event).data
                objectiveSerialized.append(objEvent)
        elif isinstance(event, MidbossEvent):
            if event.slayer:
                midbossEvent = MidbossEventSerializer(event).data
                rejuvEvent = RejuvEventSerializer(event).data
                midbossSerialized.extend([midbossEvent, rejuvEvent])
            else:
                midbossEvent = MidbossEventSerializer(event).data
                midbossSerialized.append(midbossEvent)
        else:
            continue

    matchTimeline = sorted(pvpSerialized + objectiveSerialized + midbossSerialized, key=lambda x: x['timestamp'])

    if matchPlayer:
        matchPlayerEvents = match.matchPlayerTimelineEvents.filter(player=player)

        playerSerialized = []
        for event in matchPlayerEvents:
            if isinstance(event, MatchPlayerTimelineEvent):
                if event.type == 'level':
                    levelEvent = AbilityEventSerializer(event).data
                    playerSerialized.append(levelEvent)
                elif event.type == 'item':
                    if event.details.get('sold_time_s'):
                        buyEvent = BuyEventSerializer(event).data
                        sellEvent = SellEventSerializer(event).data
                        playerSerialized.extend([buyEvent, sellEvent])
                    else:
                        serializer = BuyEventSerializer(event)
                        event_data = serializer.data
                        playerSerialized.append(event_data)
            else:
                continue

        player_pvpSerialized = [
            event for event in pvpSerialized
            if event['details']['victim'] == matchPlayer.hero_deadlock_id or event['details']['slayer'] == matchPlayer.hero_deadlock_id
        ]

        playerTimeline = sorted(player_pvpSerialized + playerSerialized + objectiveSerialized + midbossSerialized, key=lambda x: x['timestamp'])

        return Response({'matchTimeline': matchTimeline, 'playerTimeline': playerTimeline})


    return Response({'matchTimeline': matchTimeline})

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


