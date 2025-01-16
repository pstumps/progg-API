from proggbackend.services import deadlockAPIAnalyticsService, deadlockAPIDataService
from ..matches.Models.MatchesModel import MatchesModel, MatchPlayerModel
from ..players.Models.PlayerModel import PlayerModel, PlayerHeroModel


class proGGPlayersService:
    def __init__(self):
        self.DLAPIAnalyticsService = deadlockAPIAnalyticsService()
        self.DLAPIDataService = deadlockAPIDataService()

    def getRecentMatches(self, steam_id3):
        player = PlayerModel.objects.get(steam_id3=steam_id3)
        # Attempt to get last 10 match player models from our database
        proggRecentMatches = list(MatchPlayerModel.objects.filter(player=player).order_by('-match__date')[:10])

        if len(proggRecentMatches) < 10:
            dlAPIMatches = self.DLAPIAnalyticsService.getPlayerMatchHistory(steam_id3)
            for match in dlAPIMatches:
                if len(proggRecentMatches) >= 10:
                    break
                if MatchesModel.objects.filter(deadlock_id=match['match_id'], matchPlayerModel__player=player).exists():
                    matchInstance = MatchesModel.objects.get(deadlock_id=match['match_id'])
                    if not MatchPlayerModel.objects.filter(match=matchInstance, player=player).exists():
                        newMatchPlayer = self.createNewMatchPlayerFromDLAPIRecentMatch(match, matchInstance, player)
                        proggRecentMatches.append(newMatchPlayer)
                    else:
                        proggRecentMatches.append(MatchPlayerModel.objects.get(match=matchInstance, player=player))
                else:
                    newMatch = MatchesModel.objects.create(deadlock_id=match['match_id'],
                                                           length=match['match_duration_s'],
                                                           date=match['created_at'],
                                                           averageRank=match['average_match_badge'],
                                                           gameMode=match['game_mode'],
                                                           matchMode=match['match_mode'])
                    newMatch.save()

                    newMatchPlayer = self.createNewMatchPlayerFromDLAPIRecentMatch(match, newMatch, player)
                    proggRecentMatches.append(newMatchPlayer)

        return proggRecentMatches[:10]

    def createNewMatchPlayerFromDLAPIRecentMatch(self, data, match, steam_id3):
        try:
            player = PlayerModel.objects.get(steam_id3=steam_id3)
        except:
            player = None

        if data['time_abandoned_s'] > 0:
            newMatchPlayer = MatchPlayerModel.objects.create(abandoned=True,
                                                             abandonedTime=data['time_abandoned_s'],
                                                             match=match,
                                                             player=player,
                                                             steam_id3=steam_id3)
            newMatchPlayer.save()
            return newMatchPlayer
        else:
            newMatchPlayer = MatchPlayerModel.objects.create(kills=data['player_kills'],
                                                             deaths=data['player_deaths'],
                                                             assists=data['player_assists'],
                                                             hero=data['hero_id'],
                                                             team=data['player_team'],
                                                             souls=data['net_worth'],
                                                             level=data['hero_level'],
                                                             lastHits=data['last_hits'],
                                                             denies=data['denies'],
                                                             win=data['match_result'],
                                                             match=match,
                                                             player=player,
                                                             steam_id3=steam_id3)

            newMatchPlayer = self.fillInMissingMatchPlayerMetadata(newMatchPlayer)


        newMatchPlayer.save()
        return newMatchPlayer

    def fillInMissingMatchPlayerMetadata(self, matchPlayer):
        matchMetadata = self.DLAPIDataService.getMatchMetadata(dlAPIMatchId=matchPlayer.match.deadlock_id)
        if matchMetadata:
            for player in matchMetadata['match_info']['players']:
                if player['account_id'] == matchPlayer.player.steam_id3:
                    lastStat = player['stats'][-1]
                    if lastStat['time_stamp_s'] == matchPlayer.match.length:
                        matchPlayer.accuracy = round(
                            lastStat['shots_hit'] / (lastStat['shots_missed'] + lastStat['shots_hit']), 2)
                        matchPlayer.heroDamage = lastStat['player_damage']
                        matchPlayer.objDamage = lastStat['neutral_damage']
                        matchPlayer.healing = lastStat['player_healing']
                    break

        matchPlayer.save()
        return matchPlayer
