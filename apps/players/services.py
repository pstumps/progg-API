import time
from django.core.exceptions import ValidationError

from proggbackend.services.DeadlockAPIAnalytics import deadlockAPIAnalyticsService
from proggbackend.services.DeadlockAPIData import deadlockAPIDataService
from proggbackend.services.DeadlockAPIAssets import deadlockAPIAssetsService

from ..matches.services import proggAPIMatchesService
from ..matches.Models.MatchesModel import MatchesModel
from ..matches.Models.MatchPlayerModel import MatchPlayerModel
from ..players.Models.PlayerModel import PlayerModel


class proGGPlayersService:
    def __init__(self):
        self.DLAPIAnalyticsService = deadlockAPIAnalyticsService()
        self.DLAPIDataService = deadlockAPIDataService()
        self.DLAPIAssetsService = deadlockAPIAssetsService()

    def calculatePlayerHeroTiersForPlayerAndGetTopPlayerHeroes(self, steam_id3):
        player = PlayerModel.objects.filter(steam_id3=steam_id3).first()
        if player:
            player.calculatePlayerHeroTiers()

        return player.getTopPlayerHeroes()


    def getMatchHistory(self, player):
        # Internal API Only

        if not player.updated:
            matchHistory = self.DLAPIAnalyticsService.getPlayerMatchHistory(account_id=player.steam_id3, has_metadata=True)
        else:
            matchHistory = self.DLAPIAnalyticsService.getPlayerMatchHistory(account_id=player.steam_id3,
                                                                            has_metadata=True,
                                                                            min_unix_timestamp=player.updated)

        if isinstance(matchHistory, dict) and matchHistory.get('detail'):
            print(f'No new matches since last update for player {player.steam_id3}')
            return True


        if isinstance(matchHistory, list):
            DLItemsDict = self.DLAPIAssetsService.getItemsDict()
            matchesService = proggAPIMatchesService(DLItemsDict)
            if player.matches.count() != len(matchHistory):
                matchNum = 1
                for match in matchHistory:
                    if not isinstance(match, dict):
                        continue
                    if not match.get('match_id'):
                        continue
                    if MatchesModel.objects.filter(deadlock_id=match['match_id']).exists():
                        continue

                    matchMetadata = self.DLAPIDataService.getMatchMetadata(match['match_id'])
                    if matchMetadata.get('match_info'):
                        # TODO: This might be messed up, need to determine if match is already associated with player or not
                        print(f'Processing match {matchNum} of {len(matchHistory)}')
                        matchesService.createNewMatchFromMetadata(matchMetadata)
                    else:
                        print(f'Failed to get metadata for match {match["match_id"]}')
                    matchNum += 1
        else:
            print(f'Unexpected matchHistory response: {matchHistory}')
            return True

        player.updated = int(time.time())
        player.save()

        return True

    def getOrCreateValidatedSteamPlayer(self, steam_id3):
        if PlayerModel.objects.filter(steam_id3=steam_id3).first():
            return PlayerModel.objects.filter(steam_id3=steam_id3).first()

        try:
            player = PlayerModel.objects.create(steam_id3=steam_id3)
            player.save()
            return player
        except ValidationError as e:
            print(f'e: {e}')
            print(f'Player not found in steam database.')
            return None

    def deleteAllData(self):
        matchesService = proggAPIMatchesService()
        matchesService.deleteAllMatchesAndPlayersModels()


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
        matchMetadata = self.DLAPIDataService.getMatchMetadata(dl_match_id=matchPlayer.match.deadlock_id)
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
