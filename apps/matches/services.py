import datetime, json
from .Models.MatchesModel import MatchesModel
from .Models.MatchPlayerModel import MatchPlayerModel
from ..players.Models.PlayerModel import PlayerModel
from proggbackend.services import deadlockAPIAnalyticsService, deadlockAPIDataService

itemsAbilitiesDict = {}
class proggAPIMatchesService:
    def __init__(self):
        self.DLAPIAnalyticsService = deadlockAPIAnalyticsService()
        self.DLAPIDataService = deadlockAPIDataService()

    def createNewMatchFromMetadata(self, dl_match_id):
        matchMetadata = self.DLAPIDataService.getMatchMetadata(dl_match_id=dl_match_id)['match_info']
        averageBadges = {}
        badgesSum = 0

        for stat, value in matchMetadata:
            if stat.startswith('average_badge'):
                averageBadges[stat] = value
                badgesSum += value

        averageBadges['match_average_badge'] = badgesSum / len(averageBadges)

        match = MatchesModel.objects.create(
            deadlock_id=dl_match_id,
            date=datetime.datetime.fromtimestamp(matchMetadata['date'], datetime.timezone.utc),
            averageRank=json.dumps({'badges': averageBadges}),
            gameMode=matchMetadata['game_mode'],
            matchMode=matchMetadata['match_mode'],
            length=matchMetadata['duration_s'],
            victor=matchMetadata['winning_team']
        )


    def createNewMatchPlayerFromMetadata(self, playerModel, match, metadataPlayer, playerFinalItems, matchMetaData):

        endStats = metadataPlayer['stats'][-1]
        playerSouls = endStats['net_worth']
        goldSources = endStats['gold_sources']
        matchPlayer = MatchPlayerModel.objects.create(
            player=playerModel,
            match=match,
            steam_id3=metadataPlayer['account_id'],
            team=metadataPlayer['team'],
            kills=metadataPlayer['kills'],
            deaths=metadataPlayer['deaths'],
            assists=metadataPlayer['assists'],
            hero=metadataPlayer['hero_id'],
            souls=playerSouls,
            lastHits=metadataPlayer['last_hits'],
            denies=metadataPlayer['denies'],
            party=metadataPlayer['party'],
            lane=metadataPlayer['assigned_lane'],
            accuracy=endStats['shots_hit'] / endStats['shots_hit'] + endStats['shots_missed'],
            soulsBreakdown=json.dumps({
                'hero': round(playerSouls/(goldSources[0]['gold'] + goldSources[0]['gold_orbs']), 1),
                'lane_creeps': round(playerSouls/(goldSources[1]['gold'] + goldSources[1]['gold_orbs']), 1),
                'neutrals': round(playerSouls/goldSources[2]['gold'] + goldSources[2]['gold_orbs'], 1),
                'objectives': round(playerSouls/goldSources[3]['gold'] + goldSources[3]['gold_orbs']),
                'crates': round(playerSouls/goldSources[4]['gold'], 1),
                'denies': round(playerSouls/goldSources[5]['gold'], 1),
                'other': round(playerSouls/goldSources[6]['gold'], 1),
                'assists': round(playerSouls/goldSources[7]['gold'], 1)
            }),
            heroDamage=goldSources[0]['damage'],
            objDamage=goldSources[2]['damage'],
            healing=endStats['player_healing'],
            win=metadataPlayer['team'] == matchMetaData['winning_team'],
        )

    def sortPlayerItems(self, playerItems):
        abilities = []
        items = []
        for item in playerItems:
            if itemsAbilitiesDict[item].startswith('ability_'):
                abilities.append(itemsAbilitiesDict[item])


    def parseMatchEventsForMatchPlayerTimeline(self, matchMetadata):
        match_event_details = {}
        player_final_items = {player['account_id']: [] for player in matchMetadata['players']}

        player_details = {player['player_slot']: {
            'account_id': player['account_id'],
            'hero_id': player['hero_id']} for player in matchMetadata['players']}

        for player in matchMetadata['players']:
            # TODO: Only consider players where account_id exists in our db
            player_account_id = player['account_id']
            for death_event in player['death_details']:
                slayer_slot = death_event['killer_player_slot']
                slayer_info = player_details[slayer_slot]
                slayer_account_id = slayer_info['account_id']
                if slayer_account_id not in match_event_details:
                    match_event_details[slayer_account_id] = {
                        'hero_id': slayer_info['hero_id'],
                        'kills': [],
                        'deaths': [],
                        'items': []
                    }
                if player_account_id not in match_event_details:
                    match_event_details[player_account_id] = {
                        'hero_id': player['hero_id'],
                        'kills': [],
                        'deaths': [],
                        'items': []
                    }
                match_event_details[slayer_account_id]['kills'].append({
                    'victim_hero_id': player['hero_id'],
                    'time': death_event['time']
                })
                match_event_details[player_account_id]['deaths'].append({
                    'slayer_hero_id': slayer_info['hero_id'],
                    'time': death_event['time']
                })

            for item_events in player['items']:
                if player_account_id not in match_event_details:
                    match_event_details[player_account_id] = {
                        'hero_id': player['hero_id'],
                        'kills': [],
                        'deaths': [],
                        'items': []
                    }

                match_event_details[player_account_id]['items'].append({
                    'item_id': item_events['item_id'],
                    'time': item_events['game_time_s'],
                    'sold_time': item_events['sold_time_s']
                })

                if item_events['upgrade_id'] == 0 and item_events['sold_time_s'] == 0:
                    player_final_items[player_account_id].append(item_events['item_id'])



        return match_event_details

