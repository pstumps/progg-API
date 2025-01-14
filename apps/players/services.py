from proggbackend.services import deadlockAPIAnalyticsService, deadlockAPIDataService
from ..matches.Models.MatchesModel import MatchesModel, MatchPlayerModel


class proGGPlayersService:
    def __init__(self):
        self.DLAPIAnalyticsService = deadlockAPIAnalyticsService()
        self.DLAPIDataService = deadlockAPIDataService()

    def getRecentMatches(self, playerId, dlAPIPlayerId):
        dlAPIMatches = self.DLAPIAnalyticsService.getPlayerMatchHistory(dlAPIPlayerId)
        for match in dlAPIMatches:
            if MatchesModel.objects.filter(deadlock_id=match['match_id']).exists():
                continue
            else:
                newMatch = MatchesModel.objects.create(deadlock_id=match['match_id'], length=match['match_duration_s'], date=match['created_at'],
                                            averageRank=match['average_match_badge'], gameMode=match['game_mode'],
                                            matchMode=match['match_mode'])
                newMatch.save()
                newMatchPlayer = MatchPlayerModel.objects.create(kills=match['player_kills'], deaths=match['player_deaths'],
                                                                 assists=match['player_assists'], hero=match['hero_id'],
                                                                 team=match['team'], souls=match['net_worth'], level=match['hero_level'],
                                                                 lastHits=match['last_hits'],denies=match['denies'], win=match['match_result'])
                newMatchPlayer.save()


        proggMatches = MatchesModel.objects.filter(players__player_id=dlAPIPlayerId).order_by('-date')[:10]