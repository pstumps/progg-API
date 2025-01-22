import datetime, json
from django.db import transaction
from .Models.MatchesModel import MatchesModel
from .Models.MatchPlayerModel import MatchPlayerModel
from .Models.MatchPlayerTimeline import MatchPlayerTimelineEvent
from ..players.Models.PlayerModel import PlayerModel
from ..players.Models.PlayerHeroModel import PlayerHeroModel
from ..heroes.Models.HeroesModel import HeroesModel
from .Models.MatchTimeline import MatchTimelineEvent, PvPEvent, ObjectiveEvent, MidbossEvent
from proggbackend.services import deadlockAPIAnalyticsService, deadlockAPIDataService, deadlockAPIAssetsService


class proggAPIMatchesService:
    def __init__(self):
        self.DLAPIAnalytics = deadlockAPIAnalyticsService()
        self.DLAPIData = deadlockAPIDataService()
        self.DLAPIAssets = deadlockAPIAssetsService()

    @transaction.atomic
    def createNewMatchFromMetadata(self, matchMetadata):
        matchMetadata = matchMetadata['match_info']
        dl_match_id = matchMetadata['match_id']

        if MatchesModel.objects.filter(deadlock_id=dl_match_id).exists():
            return MatchesModel.objects.get(deadlock_id=dl_match_id)

        averageBadges = self.calculateAverageBadgeFromMetadata(matchMetadata)
        match = MatchesModel.objects.create(
            deadlock_id=dl_match_id,
            date=datetime.datetime.fromtimestamp(matchMetadata['start_time'], datetime.timezone.utc),
            averageRank=json.dumps({'badges': averageBadges}),
            gameMode=matchMetadata['game_mode'],
            matchMode=matchMetadata['match_mode'],
            length=matchMetadata['duration_s'],
            victor=matchMetadata['winning_team']
        )

        self.parseMatchEventsFromMetadata(match, matchMetadata)

        return match

    @transaction.atomic
    def parseMatchEventsFromMetadata(self, match, matchMetadata):
        match_event_details = {}
        accountIds = []
        midbossEvents = []
        objectiveEvents = []
        streaks = {}
        lastKillTimes = {}
        multis = {}
        streakCounts = {}
        longestStreaks = {}

        player_details = {player['player_slot']: {
            'account_id': player['account_id'],
            'hero_id': player['hero_id']} for player in matchMetadata['players']}

        for player in matchMetadata['players']:
            account_id = player['account_id']
            player_slot = player['player_slot']
            hero_id = player['hero_id']

            streaks[account_id] = 0
            lastKillTimes[account_id] = []
            multis[account_id] = [0] * 6
            streakCounts[account_id] = [0] * 8
            player_details[player_slot] = {
                'account_id': account_id,
                'hero_id': hero_id
            }

        for player in matchMetadata['players']:
            player_account_id = player['account_id']
            accountIds.append(player_account_id)

            playerToTrack = PlayerModel.objects.filter(steam_id3=player_account_id).first()
            if not playerToTrack:
                playerToTrack = PlayerModel.objects.create(
                    steam_id3=player_account_id,
                )

            abilityLevels = {}
            createTimeline = False

            if playerToTrack.timelineTracking:
                createTimeline = True

            if player.get('death_details'):
                for death_event in player['death_details']:
                    slayer_slot = death_event['killer_player_slot']
                    slayer_info = player_details[slayer_slot]
                    slayer_account_id = slayer_info['account_id']

                    # Kill streak tracking
                    if slayer_account_id not in streaks:
                        streaks[slayer_account_id] = 0
                    streaks[slayer_account_id] += 1
                    streaks[player_account_id] = 0

                    if streaks[slayer_account_id] > longestStreaks.get(slayer_account_id, 0):
                        longestStreaks[slayer_account_id] = streaks[slayer_account_id]

                    if 3 <= streaks[slayer_account_id] <= 8:
                        streakCounts[slayer_account_id][streaks[slayer_account_id] - 3] += 1
                    elif streaks[slayer_account_id] > 9:
                        streakCounts[slayer_account_id][5] += 1

                    # Multi-kill tracking
                    if slayer_account_id not in lastKillTimes:
                        lastKillTimes[slayer_account_id] = []
                    lastKillTimes[slayer_account_id].append(death_event['game_time_s'])
                    lastKillTimes[slayer_account_id] = [time for time in lastKillTimes[slayer_account_id] if
                                                        time > death_event['game_time_s'] - 5]

                    # Track each multi-kill for the slayer
                    if slayer_account_id not in multis:
                        multis[slayer_account_id] = [0] * 6

                    multiKillCount = len(lastKillTimes[slayer_account_id])
                    if multiKillCount > 1:
                        multis[slayer_account_id][min(multiKillCount, 6) - 2] += 1

                    self.createMatchTimelinePvPEvent(match, slayer_info['hero_id'], player['hero_id'],
                                                     death_event['game_time_s'], player['team'])

                    '''
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
                    '''

            for item_events in player['items']:
                if player_account_id not in match_event_details:
                    match_event_details[player_account_id] = {
                        'hero_id': player['hero_id'],
                        'items': {},
                        'abilities': [],
                    }

                item_data = self.DLAPIAssets.getItemById(item_events['item_id'])
                if item_data:
                    if item_data['class_name'].startswith('ability_'):
                        if not abilityLevels[item_data['name']]:
                            abilityLevels[item_data['name']] = []
                        else:
                            abilityLevels[item_data['name']].append(item_events['game_time_s'])

                        if createTimeline:
                            self.createMatchPlayerTimelineAbilityEvent(playerToTrack, match, item_events, item_data)

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
                            self.createMatchPlayerTimelineItemEvent(playerToTrack, match, item_events, item_data)

            sortedAbilities = sorted(abilityLevels.items(), key=lambda x: (-len(x[1]), x[1]))

            matchPlayer = self.createNewMatchPlayerFromMetadata(playerToTrack, match, player, matchMetadata)
            matchPlayer.items = json.dumps({'items': match_event_details[player_account_id]['items']})
            matchPlayer.abilities = json.dumps({'ability_order': [ability[0] for ability in sortedAbilities]})
            print('this print statement is in proggAPIMatchesService function parseMatchEventsFromMetadata')
            print(matchPlayer)
            matchPlayer.save()

        for obj in matchMetadata['objectives']:
            self.createMatchTimelineObjectiveEvent(match=match,
                                                   target=obj['team_objective_id'],
                                                   timestamp=obj['destroyed_time_s'],
                                                   team=obj['team'])

        for midboss in matchMetadata['mid_boss']:
            midbossEvents.append(self.createMatchTimelineMidbossEvent(match=match,
                                                                      slayer=midboss['team_killed'],
                                                                      team=midboss['team_claimed'],
                                                                      timestamp=midboss['destroyed_time_s']))

        for account_id in accountIds:  # multis and streaks have same keys
            matchPlayer = MatchPlayerModel.objects.get(match=match, steam_id3=account_id)
            matchPlayer.multiKills = json.dumps({'multis': multis[account_id]})
            matchPlayer.streaks = json.dumps({'streaks': streakCounts[account_id]})
            matchPlayer.save()

        return match_event_details

    def calculateAverageBadgeFromMetadata(self, metadata):
        averageBadges = {}
        badgesSum = 0

        for stat, value in metadata.items():
            if stat.startswith('average_badge'):
                averageBadges[stat] = value
                badgesSum += value

        averageBadges['match_average_badge'] = badgesSum / len(averageBadges)
        return averageBadges

    @transaction.atomic
    def createOrUpdatePlayerHero(self, matchPlayer, longestStreaks):
        playerHero = PlayerHeroModel.objects.filter(hero_id=matchPlayer.hero).first()
        hero = HeroesModel.objects.get(dl_hero_id=matchPlayer.dl_hero_id)
        if not playerHero:
            playerHero = PlayerHeroModel.objects.create(
                player=matchPlayer.player,
                hero=hero
            )
        playerHero.wins += 1 if matchPlayer.win else 0
        playerHero.matches += 1
        playerHero.kills += matchPlayer.kills
        playerHero.deaths += matchPlayer.deaths
        playerHero.assists += matchPlayer.assists
        playerHero.souls += matchPlayer.souls
        playerHero.accuracy += matchPlayer.accuracy
        playerHero.heroDamage += matchPlayer.heroDamage
        playerHero.objDamage += matchPlayer.objDamage
        playerHero.healing += matchPlayer.healing
        playerHero.longestStreak = max(playerHero.longestStreak, max(longestStreaks[matchPlayer.steam_id3]))

        return playerHero

    def updatePlayerStatsFromMatchPlayer(self, matchPlayer, multis, streaks, longestStreaks, objectiveEvents, midbossEvents):
        player = matchPlayer.player
        player.longestStreak = max(player.longestStreak, max(longestStreaks[matchPlayer.steam_id3]))
        player.midBoss += sum(1 for event in midbossEvents if event.team == matchPlayer.team)

        for event in objectiveEvents:
            if event.team == matchPlayer.team:
                if event.target.contains('tier1'):
                    player.guardians += 1
                elif event.target.contains('tier2'):
                    player.walkers += 1
                elif event.target.contains('BarracksBoss'):
                    player.baseGuardians += 2
                elif event.target.contains('TitanShieldGenerator'):
                    player.shieldGenerators += 1
                elif event.target.contains('k_eCitadelTeamObjective_Core'):
                    player.patrons += 1

        if any(multis[matchPlayer.steam_id3]):
            if not player.multis:
                player.multis = json.dumps({'multis': multis[matchPlayer.steam_id3]})
            else:
                player.multis = json.dumps({'multis': [sum(x) for x in zip(json.loads(player.multis)['multis'],
                                                                               multis[matchPlayer.steam_id3])]})
        else:
            player.multis = None

        if any(streaks[matchPlayer.steam_id3]):
            if not player.streaks:
                player.streaks = json.dumps({'streaks': streaks[matchPlayer.steam_id3]})
            else:
                player.streaks = json.dumps({'streaks': [sum(x) for x in zip(json.loads(player.streaks)['streaks'],
                                                                                streaks[matchPlayer.steam_id3])]})
        else:
            player.streaks = None

        return player

    @transaction.atomic
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
                'soul_sources': {
                    'hero': round(playerSouls / (goldSources[0]['gold'] + goldSources[0]['gold_orbs']), 1),
                    'lane_creeps': round(playerSouls / (goldSources[1]['gold'] + goldSources[1]['gold_orbs']), 1),
                    'neutrals': round(playerSouls / goldSources[2]['gold'] + goldSources[2]['gold_orbs'], 1),
                    'objectives': round(playerSouls / goldSources[3]['gold'] + goldSources[3]['gold_orbs']),
                    'crates': round(playerSouls / goldSources[4]['gold'], 1),
                    'denies': round(playerSouls / goldSources[5]['gold'], 1),
                    'other': round(playerSouls / goldSources[6]['gold'], 1),
                    'assists': round(playerSouls / goldSources[7]['gold'], 1)
                }
            }),
            heroDamage=goldSources[0]['damage'],
            objDamage=goldSources[2]['damage'],
            healing=endStats['player_healing'],
            win=playerMetadata['team'] == matchMetaData['winning_team'],
        )
        return matchPlayer

    @transaction.atomic
    def createMatchPlayerTimelineItemEvent(self, player, match, item_event, item_data):
        if item_data:
            MatchPlayerTimelineEvent.objects.create(
                match=match,
                player=player,
                timestamp=item_event['game_time_s'],
                eventType='item',
                eventData={'item_id': item_event['item_id'],
                           'target': item_data['name'],
                           'slot': item_data['item_slot_type'],
                           'sold_time_s': item_event['sold_time_s']}
            )

    @transaction.atomic
    def createMatchPlayerTimelineAbilityEvent(self, player, match, item_event, item_data):
        if item_data:
            MatchPlayerTimelineEvent.objects.create(
                match=match,
                player=player,
                timestamp=item_event['game_time_s'],
                eventType='level',
                eventData={'ability_id': item_event['item_id'],
                           'target': item_data['name']}
            )

    @transaction.atomic
    def createMatchTimelinePvPEvent(self, match, slayer_hero_id, victim_hero_id, timestamp, team):
        PvPEvent.objects.create(
            match=match,
            timestamp=timestamp,
            team=team,
            slayer_hero_id=slayer_hero_id,
            victim_hero_id=victim_hero_id
        )

    @transaction.atomic
    def createMatchTimelineObjectiveEvent(self, match, target, timestamp, team):
        objectiveEvent = ObjectiveEvent.objects.create(
            match=match,
            timestamp=timestamp,
            team=team,
            target=target
        )

        objectiveEvent.save()
        return objectiveEvent

    @transaction.atomic
    def createMatchTimelineMidbossEvent(self, match, slayer, timestamp, team):
        midbossEvent = MidbossEvent.objects.create(
            match=match,
            timestamp=timestamp,
            team=team,
            slayer=slayer
        )

        midbossEvent.save()
        return midbossEvent
