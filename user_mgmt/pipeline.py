from django.db import transaction
from django.contrib.auth import login
from apps.players.Models.PlayerModel import PlayerModel
from django.shortcuts import redirect
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken

@transaction.atomic
def connect_steam_account(response, strategy, details, user=None, social=None, *args, **kwargs):
    if not user:
        return

    steam_id64 = social.uid if social else None
    if not steam_id64:
        return

    steam_id3 = convertSteamID64ToSteamID3(steam_id64)

    player, created = PlayerModel.objects.get_or_create(steam_id3=steam_id3)

    if player.user != user:
        player.user = user
        player.save()

def convertSteamID64ToSteamID3(steam_id64):
    steamid64ident = 76561197960265728
    steam_id3 =  int(steam_id64) - steamid64ident
    return steam_id3


def social_auth_redirect(strategy, backend, user, response, *args, **kwargs):
    print("Authenticated user:", user)
    if not user:
        return redirect(f"{settings.NEXTJS_FRONTEND_URL}/login-failed")


    # Retrieve next parameter
    next_url = strategy.session_get('next') or strategy.request_data().get('next') or "/"

    # Redirect to Next.js frontend
    frontend_base = settings.NEXTJS_FRONTEND_URL
    return redirect(f"{frontend_base}{next_url}")