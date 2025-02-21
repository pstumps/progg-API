from django.shortcuts import redirect
from django.contrib.auth import login
from social_django.utils import load_strategy, load_backend
from social_core.actions import do_auth
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db import transaction
from apps.players.Models.PlayerModel import PlayerModel



@api_view(['GET'])
def userAuth(request):
    print(request)
    print("Authenticated user:", request.user)
    if request.user.is_authenticated:
        print('user id is ', request.user.id)
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
    if request.user.is_authenticated:
        return Response({
            'name': request.user.playermodel.name,
            'icon': request.user.playermodel.icon,
            'steam_id3': request.user.playermodel.steam_id3,
        }, status=200)
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
        player.save()
        print("Successfully connected account for player ", player.name)

def convertSteamID64ToSteamID3(steam_id64):
    steamid64ident = 76561197960265728
    steam_id3 = int(steam_id64) - steamid64ident
    return steam_id3

