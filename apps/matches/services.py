import datetime, json
from .Models.MatchesModel import MatchesModel
from .Models.MatchPlayerModel import MatchPlayerModel
from .Models.MatchPlayerTimeline import MatchPlayerTimelineEvent
from ..players.Models.PlayerModel import PlayerModel
from .Models.MatchTimeline import MatchTimelineEvent
from proggbackend.services import deadlockAPIAnalyticsService, deadlockAPIDataService, deadlockAPIAssetsService

class proggAPIMatchesService:
    def __init__(self):
        self.DLAPIAnalytics = deadlockAPIAnalyticsService()
        self.DLAPIData = deadlockAPIDataService()
        self.DLAPIAssets = deadlockAPIAssetsService()

    def createNewMatchFromMetadata(self, dl_match_id):
        matchMetadata = self.DLAPIData.getMatchMetadata(dl_match_id=dl_match_id)['match_info']
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


    def createNewMatchPlayerFromMetadata(self, playerModel, match, playerMetadata, matchMetaData):
        endStats = playerMetadata['stats'][-1]
        playerSouls = endStats['net_worth']
        goldSources = endStats['gold_sources']
        matchPlayer = MatchPlayerModel.objects.create(
            player=playerModel,
            match=match,
            steam_id3=playerMetadata['account_id'],
            team=playerMetadata['team'],
            playerSlot=playerMetadata['player_slot'],
            kills=playerMetadata['kills'],
            deaths=playerMetadata['deaths'],
            assists=playerMetadata['assists'],
            hero=playerMetadata['hero_id'],
            souls=playerSouls,
            lastHits=playerMetadata['last_hits'],
            denies=playerMetadata['denies'],
            party=playerMetadata['party'],
            lane=playerMetadata['assigned_lane'],
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
            win=playerMetadata['team'] == matchMetaData['winning_team'],
        )
        return matchPlayer


    def parseMatchEventsFromMetadata(self, match, matchMetadata):
        match_event_details = {}

        player_details = {player['player_slot']: {
            'account_id': player['account_id'],
            'hero_id': player['hero_id']} for player in matchMetadata['players']}

        for player in matchMetadata['players']:
            player_account_id = player['account_id']

            playerToTrack = PlayerModel.objects.filter(steam_id3=player_account_id).first()
            if not playerToTrack:
                playerToTrack = PlayerModel.objects.create(
                    steam_id3=player_account_id,
                    )

            abilityLevels = {}
            createTimeline = False

            if playerToTrack.timelineTracking:
                createTimeline = True

            for death_event in player['death_details']:
                slayer_slot = death_event['killer_player_slot']
                slayer_info = player_details[slayer_slot]
                slayer_account_id = slayer_info['account_id']
                if slayer_account_id not in match_event_details:
                    match_event_details[slayer_account_id] = {
                        'hero_id': slayer_info['hero_id'],
                        'kills': [],
                        'deaths': [],
                        'items': {}
                    }
                if player_account_id not in match_event_details:
                    match_event_details[player_account_id] = {
                        'hero_id': player['hero_id'],
                        'kills': [],
                        'deaths': [],
                        'items': {}
                    }
                match_event_details[slayer_account_id]['kills'].append({
                    'victim_hero_id': player['hero_id'],
                    'time': death_event['game_time_s']
                })
                match_event_details[player_account_id]['deaths'].append({
                    'slayer_hero_id': slayer_info['hero_id'],
                    'time': death_event['game_time_s']
                })

                MatchTimelineEvent.objects.create(
                    match=match,
                    timestamp=death_event['time'],
                    eventType='pvp',
                    eventData={'slayer_hero_id': slayer_info['hero_id'],
                               'victim_hero_id': player['hero_id']}
                )

                if createTimeline:
                    MatchPlayerTimelineEvent.objects.create(
                       match=match,
                       player=playerToTrack,
                       timestamp=death_event['game_time_s'],
                       eventType='pvp',
                       eventData={'slayer_hero_id': slayer_info['hero_id'],
                                  'victim_hero_id': player['hero_id']}
                    )

                if slayer_account_id == playerToTrack.steam_id3:
                    if createTimeline:
                        MatchPlayerTimelineEvent.objects.create(
                            match=match,
                            player=playerToTrack,
                            timestamp=death_event['game_time_s'],
                            eventType='pvp',
                            eventData={'slayer_hero_id': slayer_info['hero_id'],
                                       'victim_hero_id': player['hero_id']}
                        )

            for item_events in player['items']:

                if player_account_id not in match_event_details:
                    match_event_details[player_account_id] = {
                        'hero_id': player['hero_id'],
                        'kills': [],
                        'deaths': [],
                        'items': {},
                        'abilities': []
                    }

                item_data = self.DLAPIAssets.getItemById(item_events['item_id'])

                if item_data:

                    if item_data['class_name'].startswith('ability_'):
                        if not abilityLevels[item_data['name']]:
                            abilityLevels[item_data['name']] = []
                        else:
                            abilityLevels[item_data['name']].append(item_events['game_time_s'])

                        if createTimeline:
                            MatchPlayerTimelineEvent.objects.create(
                                match=match,
                                player=playerToTrack,
                                timestamp=item_events['game_time_s'],
                                eventType='level',
                                eventData={'ability_id': item_events['item_id'],
                                           'target': item_data['name']}
                            )
                    elif item_data.get('item_slot_type'):
                        playerItemsDictionary = match_event_details[player_account_id]['items']
                        if item_events['sold_time_s'] == 0 and item_events['upgrade_id'] == 0:
                            # Item was a part of final build
                            if item_data['item_slot_type'] not in playerItemsDictionary:
                                playerItemsDictionary[item_data['item_slot_type']] = []
                            if len(playerItemsDictionary[item_data['item_slot_type']]) == 4:
                                if not playerItemsDictionary.get('flex'):
                                    playerItemsDictionary['flex'] = []
                                else:
                                    playerItemsDictionary['flex'].append({
                                        'item_id': item_events['item_id'],
                                        'target': item_data['name'],
                                        'type': item_data['item_slot_type']
                                    })
                            playerItemsDictionary[item_data['item_slot_type']].append({
                                'item_id': item_events['item_id'],
                                'target': item_data['name'],
                            })
                        if createTimeline:
                            MatchPlayerTimelineEvent.objects.create(
                                match=match,
                                player=playerToTrack,
                                timestamp=item_events['game_time_s'],
                                eventType='item',
                                eventData={'item_id': item_events['item_id'],
                                           'target': item_data['name'],
                                           'slot': item_data['item_slot_type'],
                                           'sold_time_s': item_events['sold_time_s']}
                            )

            sortedAbilities = sorted(abilityLevels.items(), key=lambda x: (-len(x[1]), x[1]))
            matchPlayer = self.createNewMatchPlayerFromMetadata(playerToTrack, match, player, matchMetadata)
            matchPlayer.items = json.dumps({'items': match_event_details[player_account_id]['items']})
            matchPlayer.abilities = json.dumps({'ability_order': [ability[0] for ability in sortedAbilities]})
            matchPlayer.save()

        for obj in matchMetadata['objectives']:
            MatchTimelineEvent.objects.create(
                match=match,
                timestamp=obj['destroyed_time_s'],
                eventType='obj',
                eventData={'target': obj['team_objective_id'], 'team': obj['team']}
            )

        for midboss in matchMetadata['mid_boss']:
            MatchTimelineEvent.objects.create(
                match=match,
                timestamp=midboss['destroyed_time_s'],
                eventType='midboss',
                eventData={'killed': midboss['team_killed'], 'claimed': midboss['team_claimed']}
            )


        return match_event_details

