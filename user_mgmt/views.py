from django.shortcuts import redirect
from django.contrib.auth import login, logout
from social_django.utils import load_strategy, load_backend
from social_core.actions import do_auth
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from apps.players.Models.PlayerModel import PlayerModel
from apps.matches.Models.MatchesModel import MatchesModel
from user_mgmt.serializers import UserSerializer
from rest_framework import status

import time



@api_view(['GET'])
def userAuth(request):
    if request.user.is_authenticated:
        return Response({
            'id': request.user.id,
            'username': request.user.username
        }, status=200)
    else:
        return Response({
            'detail': 'User is not authenticated'
        }, status=401)


@api_view(['GET'])
def getUserInfo(request):
    user = request.user
    if user.is_authenticated:
        if user.playermodel is None:
            return Response({
                'detail': 'User has no playermodel'
            }, status=404)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=200)
    else:
        return Response({
            'detail': 'User is not authenticated'
        }, status=401)


def steam_login(request):
    strategy = load_strategy(request)
    backend = load_backend(strategy=strategy, name='steam', redirect_uri='http://127.0.0.1:8080/user_mgmt/auth/steam/callback')
    return do_auth(backend, redirect_name='next')


def steam_callback(request):
    print("Steam callback")
    strategy = load_strategy(request)
    backend = load_backend(strategy=strategy, name='steam', redirect_uri='http://127.0.0.1:8080/user_mgmt/auth/steam/callback')
    user = backend.complete(user=None)

    if user and hasattr(user, 'is_authenticated') and user.is_authenticated:
        login(request, user)

        if not hasattr(user, 'playermodel') or user.playermodel is None:
            connect_steam_account(request, user)

        user.playermodel.lastLogin = int(time.time())

        response = redirect("http://localhost:3000/")
        response.set_cookie(
            key="sessionid",
            value=request.session.session_key,
            httponly=True,
            samesite="None",
            secure=False
        )
        return response


    return Response({'error': 'Authentication failed'}, status=401)

@transaction.atomic
def connect_steam_account(request, user):
    if not user:
        return
    print('connecting steam account for ', user)

    social = user.social_auth.get(provider='steam')
    if not social:
        return

    steam_id64 = social.uid
    steam_id3 = convertSteamID64ToSteamID3(steam_id64)
    player, created = PlayerModel.objects.get_or_create(steam_id3=steam_id3)

    if player.user != user:
        player.user = user
        player.active = False
        player.lastLogin = int(time.time())
        player.save()
        print("Successfully connected account for player ", player.name)

def convertSteamID64ToSteamID3(steam_id64):
    steamid64ident = 76561197960265728
    steam_id3 = int(steam_id64) - steamid64ident
    return steam_id3

@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def favorites_player(request, player_id):
    user = request.user
    player = get_object_or_404(PlayerModel, steam_id3=player_id)

    if request.method == 'POST':
        if player.steam_id3 not in user.favorites.values_list('id', flat=True):
            user.favorites.add(player)
        return Response({"message": "Added to favorites"}, status=201)

    elif request.method == 'DELETE':
        user.favorites.remove(player)
        return Response({"message": "Removed from favorites"}, status=200)

    return Response({"error": "Invalid request"}, status=400)

@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def favorites_match(request, match_id):
    user = request.user
    match = get_object_or_404(MatchesModel, deadlock_id=match_id)

    if request.method == 'POST':
        if match.deadlock_id not in user.match_favorites.values_list('id', flat=True):
            user.match_favorites.add(match)
        return Response({"message": "Added to favorites"}, status=201)

    elif request.method == 'DELETE':
        user.match_favorites.remove(match)
        return Response({"message": "Removed from favorites"}, status=200)

    return Response({"error": "Invalid request"}, status=400)

@api_view(['POST'])
def logout_view(request):
    request.session.flush()
    return Response(status=status.HTTP_204_NO_CONTENT)
