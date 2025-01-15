from django.shortcuts import render
from .services import proGGPlayersService

def recentMatches(request, steam_id3):
    playersService = proGGPlayersService()
    lastTenMatches = playersService.getRecentMatches(steam_id3)

    # Check if player data is missing- a player has played a match but we don't have their metadata
    for recentMatch in lastTenMatches:
        if not recentMatch.abandoned:
            if recentMatch.accuracy == 0:
                playersService.fillInMissingMatchPlayerMetadata(recentMatch)

    return {'recentMatches': lastTenMatches}
