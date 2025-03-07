import time
from django.db import transaction
from apps.matches.Models.MatchesModel import MatchesModel
from apps.matches.Models.MatchPlayerModel import MatchPlayerModel
from apps.matches.Models.MatchPlayerTimeline import MatchPlayerTimelineEvent
from apps.matches.Models.MatchPlayerGraph import MatchPlayerGraph
from apps.players.Models.PlayerModel import PlayerModel
from apps.matches.Models.MatchTimeline import PvPEvent, ObjectiveEvent, MidbossEvent
from proggbackend.services.DeadlockAPIAnalytics import deadlockAPIAnalyticsService
from proggbackend.services.DeadlockAPIData import deadlockAPIDataService
from proggbackend.services.DeadlockAPIAssets import deadlockAPIAssetsService


def calculateAverageBadgeFromMetadata(metadata):
    averageBadges = {}
    badgesSum = 0

    for stat, value in metadata.items():
        if stat.startswith('average_badge'):
            averageBadges[stat] = value
            badgesSum += value

    if averageBadges:
        averageBadges['match_average_badge'] = int(badgesSum / len(averageBadges))
        return averageBadges
    return None


class MetadataServices:
    def __init__(self, DLItemsDict=None):
        self.DLAPIAnalytics = deadlockAPIAnalyticsService()
        self.DLAPIData = deadlockAPIDataService()
        self.DLAPIAssets = deadlockAPIAssetsService()
        self.DLItemsDict = DLItemsDict

    @transaction.atomic
    def createNewMatchFromMetadata(self, matchMetadata):

        matchMetadata = matchMetadata.get('match_info')
        if matchMetadata:
            dl_match_id = matchMetadata.get('match_id')

            try:
                existingMatch = MatchesModel.objects.get(deadlock_id=dl_match_id)
            except MatchesModel.DoesNotExist:
                existingMatch = None

            if existingMatch:
                return existingMatch

            averageBadges = calculateAverageBadgeFromMetadata(matchMetadata)
            match = MatchesModel.objects.create(
                deadlock_id=dl_match_id,
                date=matchMetadata.get('start_time') if matchMetadata.get('start_time') else None,
                averageRank=averageBadges if averageBadges else None,
                gameMode=matchMetadata.get('game_mode'),
                matchMode=matchMetadata.get('match_mode'),
                length=matchMetadata.get('duration_s'),
                victor=matchMetadata.get('winning_team'),
            )

            legacyFourLaneMap = False
            if int(matchMetadata.get('start_time')) < 1740549073:
                match.legacyFourLaneMap = True

            self.parseMatchEventsFromMetadata(match, matchMetadata, legacyFourLaneMap)

            match.calculateTeamStats()
            match.save()
            print('Match created successfully!')

            return match
        else:
            print('Invalid Metadata. Metadata does not contain match_info.')
            return None

    @transaction.atomic
    def parseMatchEventsFromMetadata(self, match, matchMetadata, legacyFourLaneMap=False):
        print('Parsing match metadata...')
        matchPlayerData = {}
        pvpEvents = []
        playerStatsGraphs = []
        playerEvents = []
        streaks = {}
        lastKillTimes = {}
        multis = {}
        streakCounts = {}
        longestStreaks = {}
        player_details = {}

        all_account_ids = [p['account_id'] for p in matchMetadata['players']]
        existing_players = PlayerModel.objects.in_bulk(all_account_ids, field_name='steam_id3')
        players_to_create = []
        for acct_id in all_account_ids:
            if acct_id not in existing_players:
                players_to_create.append(PlayerModel(steam_id3=acct_id))
        PlayerModel.objects.bulk_create(players_to_create)
        all_players = {p.steam_id3: p for p in PlayerModel.objects.filter(steam_id3__in=all_account_ids)}

        for player in matchMetadata['players']:
            abandonTime = None
            if player.get('stats'):
                abandonTime = self.checkForAbandonment(stats=player.get('stats'))

            account_id = player['account_id']
            playerToTrack = all_players[account_id]
            player_slot = player['player_slot']
            hero_id = player['hero_id']

            streaks[account_id] = 0
            lastKillTimes[account_id] = {
                'prev_time': None,
                'consecutive_count': 0
            }
            multis[account_id] = [0] * 6
            streakCounts[account_id] = [0] * 7
            player_details[player_slot] = {
                'account_id': account_id,
                'hero_id': hero_id
            }

            if account_id not in matchPlayerData:
                if abandonTime is not None:
                    matchPlayerData[account_id] = self.createMatchPlayer(player, playerToTrack, match, matchMetadata, abandoned=abandonTime)
                else:
                    matchPlayerData[account_id] = self.createMatchPlayerData(player, playerToTrack, match, matchMetadata)

            if player.get('items'):
                for item_events in player.get('items'):
                    self.processItemEvents(item_events, matchPlayerData, account_id, playerEvents)

            # map was 4 lanes instead of new 3
            if legacyFourLaneMap:
                endStatsData = self.computePlayerMetadata(matchMetadata, player, legacy=True)
            else:
                endStatsData = self.computePlayerMetadata(matchMetadata, player)


            matchPlayerData[account_id].update(endStatsData)

        # Process death details
        all_deaths = []
        for player in matchMetadata['players']:
            if player.get('death_details'):
                for death_event in player['death_details']:
                    slayer_slot = death_event.get('killer_player_slot')
                    if slayer_slot is not None:
                        all_deaths.append({
                            'game_time_s': death_event['game_time_s'],
                            'slayer_slot': slayer_slot,
                            'victim_slot': player['player_slot'],
                            'team': player['team'],
                        })
        all_deaths.sort(key=lambda x: x['game_time_s'])
        self.processDeathDetails(all_deaths, player_details, streaks, lastKillTimes, multis, streakCounts,
                                 longestStreaks,
                                 match, pvpEvents)

        # Process objectives and midboss events
        objectiveEvents, midbossEvents = self.processObjectivesAndMidbossEvents(match, matchMetadata)

        #Create all objects
        PvPEvent.objects.bulk_create(pvpEvents)
        ObjectiveEvent.objects.bulk_create(objectiveEvents)
        MidbossEvent.objects.bulk_create(midbossEvents)
        MatchPlayerTimelineEvent.objects.bulk_create(playerEvents)

        #Create Match Players
        matchPlayersToCreate = []
        for account_id, data in matchPlayerData.items():
            matchPlayersToCreate = self.createMatchPlayer(matchPlayersToCreate, data, multis.get(account_id),
                                                          streakCounts.get(account_id))
            player = data['playerModel']

            playerHero = player.getOrCreatePlayerHero(data['hero_deadlock_id'])

            playerHero.updateFromMatchPlayerStats(data, longestStreaks.get(account_id, 0))
            playerHero.updateMultisStreaksStats(multis.get(account_id), streakCounts.get(account_id))
            playerHero.updateMidbossStats(data['team'], midbossEvents)

            # Objective IDs changed after this patch day
            if legacyFourLaneMap:
                playerHero.updateLegacyTeamObjectiveStats(data['team'], objectiveEvents)
            else:
                playerHero.updateTeamObjectiveStats(data['team'], objectiveEvents)

            playerHero.save()


            player.updatePlayerRecords(data['hero_deadlock_id'],
                                       data['kills'],
                                       data['assists'],
                                       data['souls'],
                                       data['heroDamage'],
                                       data['objDamage'],
                                       data['healing'],
                                       data['lastHits'])

            player.addMatch(match)

            player.save()

        MatchPlayerGraph.objects.bulk_create(playerStatsGraphs)
        MatchPlayerModel.objects.bulk_create(matchPlayersToCreate)

        if matchPlayersToCreate:
            self.getMedals(matchPlayersToCreate)

            MatchPlayerModel.objects.bulk_update(matchPlayersToCreate, ['medals'])

        return matchPlayerData

    def processDeathDetails(self, all_deaths, player_details, streaks, lastKillTimes,
                            multis, streakCounts, longestStreaks, match, pvpEvents):
        for death_event in all_deaths:
            slayer_slot = death_event.get('slayer_slot')
            if slayer_slot is None:
                continue

            slayer_info = player_details.get(slayer_slot)
            if slayer_info is None:
                continue

            slayer_account_id = slayer_info['account_id']

            victim_slot = death_event.get('victim_slot')
            if victim_slot is None:
                continue

            victim_info = player_details[victim_slot]
            victim_account_id = victim_info['account_id']

            # Kill streak tracking
            if slayer_account_id not in streaks:
                streaks[slayer_account_id] = 0
            streaks[slayer_account_id] += 1
            streaks[victim_account_id] = 0

            if streaks[slayer_account_id] > longestStreaks.get(slayer_account_id, 0):
                longestStreaks[slayer_account_id] = streaks[slayer_account_id]

            if 3 <= streaks[slayer_account_id] <= 8:
                streakCounts[slayer_account_id][streaks[slayer_account_id] - 3] += 1

            streakCounts[slayer_account_id][6] = max(
                streakCounts[slayer_account_id][6],
                streaks[slayer_account_id]
            )

            if slayer_account_id not in lastKillTimes:
                lastKillTimes[slayer_account_id] = {
                    'prev_time': None,
                    'consecutive_count': 0
                }

            prev_time = lastKillTimes[slayer_account_id]['prev_time']

            if prev_time is None or (death_event['game_time_s'] - prev_time > 5):
                # More than 5s since last kill => reset
                lastKillTimes[slayer_account_id]['consecutive_count'] = 1
            else:
                # Within 5s => increment the chain
                lastKillTimes[slayer_account_id]['consecutive_count'] += 1

            current_count = lastKillTimes[slayer_account_id]['consecutive_count']
            # If it's at least a "Double Kill" (2 or more)
            if current_count >= 2:
                multis[slayer_account_id][min(current_count, 7) - 2] += 1

            # Update 'prev_time' to the current kill's time
            lastKillTimes[slayer_account_id]['prev_time'] = death_event['game_time_s']

            if match.date >= int(time.time()) - 1296000:
                pvpEvents.append(
                    PvPEvent(
                        match=match,
                        timestamp=death_event['game_time_s'],
                        team=death_event.get('team'),
                        slayer_hero_id=slayer_info['hero_id'],
                        victim_hero_id=victim_info['hero_id']
                    )
                )

    def processItemEvents(self, item_events, matchPlayerData, account_id, playerEvents):

        item_data = self.DLItemsDict.get(item_events['item_id'])
        if not item_data:
            return

        playerDict = matchPlayerData[account_id]
        if item_data.get('type') == 'ability':
            if item_data['name'] not in playerDict['abilities']:
                playerDict['abilities'][item_data['name']] = []
            else:
                playerDict['abilities'][item_data['name']].append(item_events['game_time_s'])

            if playerDict['playerModel'].isUser and playerDict['playerModel'].isInactive() is False:
                self.handleMatchPlayerTimelineAbilityEvent(playerDict['playerModel'], playerDict['match'], item_events,
                                                           item_data, playerEvents)

        elif item_data.get('type') == 'upgrade':
            playerItemsDictionary = playerDict['items']
            if item_events['sold_time_s'] == 0 and item_events['upgrade_id'] == 0:
                # Item was a part of final build
                if item_data['item_slot_type'] not in playerItemsDictionary:
                    playerItemsDictionary[item_data['item_slot_type']] = []
                if len(playerItemsDictionary[item_data['item_slot_type']]) >= 4:
                    if not playerItemsDictionary.get('flex'):
                        playerItemsDictionary['flex'] = []
                    playerItemsDictionary['flex'].append(
                        item_data['id']
                    )
                else:
                    playerItemsDictionary[item_data['item_slot_type']].append(item_data['id'])
            if playerDict['playerModel'].isUser and playerDict['playerModel'].isInactive() is False:
                self.handleMatchPlayerTimelineItemEvent(playerDict['playerModel'], playerDict['match'], item_events,
                                                        item_data, playerEvents)

    def processObjectivesAndMidbossEvents(self, match, matchMetadata):
        objectiveEvents = []
        midbossEvents = []

        if matchMetadata.get('objectives'):
            for obj in matchMetadata['objectives']:
                objectiveEvents.append(ObjectiveEvent(match=match,
                                                      target=obj['team_objective_id'],
                                                      timestamp=obj['destroyed_time_s'],
                                                      team=obj['team']))
        if matchMetadata.get('mid_boss'):
            for midboss in matchMetadata['mid_boss']:
                midbossEvents.append(MidbossEvent(match=match,
                                                  slayer=midboss['team_killed'],
                                                  team=midboss['team_claimed'],
                                                  timestamp=midboss['destroyed_time_s']))

        return objectiveEvents, midbossEvents

    def getPlayerGraphs(self, metadata):
        statsGraphs = {}
        teamDict = {}
        souls, heroDmg, objDmg, healing = [], [], [], []
        matchInfo = metadata.get('match_info')
        if matchInfo:
            for player in matchInfo['players']:
                hero_id = player['hero_id']
                team = player.get('team')
                lane = player.get('assigned_lane')
                if team not in teamDict:
                    teamDict[team] = {}
                if lane not in teamDict[team]:
                    teamDict[team][lane] = [hero_id]
                else:
                    teamDict[team][lane].append(hero_id)

                stats = player.get('stats')
                if stats:
                    for stat in stats:
                        time = stat['time_stamp_s']

                        if time not in statsGraphs:
                            statsGraphs[time] = {
                            }
                        player_data = {
                            'souls': stat.get('net_worth', 0),
                            'heroDmg': stat.get('player_damage', 0),
                            'objDmg': stat.get('boss_damage', 0),
                            'healing': stat.get('player_healing', 0)
                        }

                        statsGraphs[time][hero_id] = player_data

            for t, d in statsGraphs.items():
                souls.append({'timestamp': t, **{k: v['souls'] for k, v in d.items()}})
                heroDmg.append({'timestamp': t, **{k: v['heroDmg'] for k, v in d.items()}})
                objDmg.append({'timestamp': t, **{k: v['objDmg'] for k, v in d.items()}})
                healing.append({'timestamp': t, **{k: v['healing'] for k, v in d.items()}})

            print('Graphs created successfully!')
            data = {'teamKey': teamDict,
                    'graphs': {
                        'souls': souls,
                        'heroDmg': heroDmg,
                        'objDmg': objDmg,
                        'healing': healing
                        },
                    }
            return data

        return None

    def checkForAbandonment(self, stats):
        if len(stats) - 2 < 0:
            return None
        for i in range(len(stats) - 2):
            if (stats[i]['time_stamp_s'] > stats[i + 1]['time_stamp_s'] and
                    stats[i].get('shots_hit') == stats[i + 1].get('shots_hit') and
                    stats[i].get('shots_missed') == stats[i+1].get('shots_missed') and
                    stats[i].get('player_damage') == stats[i+1].get('player_damage') and
                    stats[i].get('creep_damage') == stats[i+1].get('creep_damage')):
                # Player must be doing nothing
                return stats[i]['time_stamp_s']
        return None

    def computePlayerMetadata(self, matchMetadata, playerMetadata, legacyFourLaneMap=False):
        match_info = matchMetadata
        match_length = match_info.get('duration_s', 1) or 1
        end_stats = playerMetadata['stats'][-1]

        playerSouls = end_stats.get('net_worth', 0)
        accuracy = 0
        totalShots = end_stats.get('shots_hit', 0) + end_stats.get('shots_missed', 0)
        if totalShots > 0:
            accuracy = round(end_stats['shots_hit'] / totalShots, 4)

        heroCritPercent = 0
        if end_stats.get('hero_bullets_hit'):
            heroCritPercent = round(end_stats['hero_bullets_hit_crit'] / end_stats['hero_bullets_hit'], 4)

        def getGold(goldSources, index, includeOrbs=True):
            try:
                source = goldSources[index]
            except (IndexError, TypeError):
                return 0
            gold = source.get('gold', 0)
            if includeOrbs:
                gold += source.get('gold_orbs', 0)
            return gold

        if legacyFourLaneMap:
            # gold mappings changed after this time
            goldMapping = {
                'hero': (0, True),
                'lane_creeps': (1, True),
                'neutrals': (2, True),
                'objectives': (3, True),
                'crates': (4, False),
                'denies': (5, False),
                'other': (6, False),
                'assists': (7, False)
            }
        else:
            goldMapping = {
                'hero': (0, True),
                'lane_creeps': (1, True),
                'neutrals': (2, True),
                'objectives': (3, True),
                'crates': (4, False),
                'assists': (7, False),
                'denies': (5, False),
                'other': (6, False)
            }

        if playerSouls > 0:
            soulsBreakdown = {
                key: getGold(end_stats.get('gold_sources', []), idx, incOrbs)
                for key, (idx, incOrbs) in goldMapping.items()
            }
        else:
            soulsBreakdown = {k: 0 for k in goldMapping.keys()}

        return {
            'souls': playerSouls,
            'soulsPerMin': round(playerSouls / (match_length / 60), 2),
            'laneCreeps': end_stats.get('creep_kills', 0),
            'neutralCreeps': end_stats.get('neutral_kills', 0),
            'accuracy': accuracy,
            'heroCritPercent': heroCritPercent,
            'soulsBreakdown': soulsBreakdown,
            'heroDamage': end_stats.get('player_damage', 0),
            'objDamage': end_stats.get('boss_damage', 0),
            'healing': end_stats.get('player_healing', 0),
        }

    def getMedals(self, matchPlayersToCreate):
        top_kills_val = max(p.kills for p in matchPlayersToCreate)
        top_kills_players = [p for p in matchPlayersToCreate if p.kills == top_kills_val]
        top_hero_damage_val = max(p.heroDamage for p in matchPlayersToCreate)
        top_hero_damage_players = [p for p in matchPlayersToCreate if p.heroDamage == top_hero_damage_val]
        top_souls_val = max(p.souls for p in matchPlayersToCreate)
        top_souls_players = [p for p in matchPlayersToCreate if p.souls == top_souls_val]
        top_assists_val = max(p.assists for p in matchPlayersToCreate)
        top_assists_players = [p for p in matchPlayersToCreate if p.assists == top_assists_val]
        top_obj_damage_val = max(p.objDamage for p in matchPlayersToCreate)
        top_obj_damage_players = [p for p in matchPlayersToCreate if p.objDamage == top_obj_damage_val]
        top_healing_val = max(p.healing for p in matchPlayersToCreate)
        top_healing_players = [p for p in matchPlayersToCreate if p.healing == top_healing_val]

        for p in top_kills_players:
            p.medals = (p.medals or []) + ['slays']
        for p in top_hero_damage_players:
            p.medals = (p.medals or []) + ['heroDmg']
        for p in top_souls_players:
            p.medals = (p.medals or []) + ['souls']
        for p in top_assists_players:
            p.medals = (p.medals or []) + ['assists']
        for p in top_obj_damage_players:
            p.medals = (p.medals or []) + ['objDmg']
        for p in top_healing_players:
            p.medals = (p.medals or []) + ['healing']

    def handleMatchPlayerTimelineItemEvent(self, player, match, item_event, item_data, playerTimelineEvents):
        if item_data:
            itemDetails = {'target': item_data['name'],
                           'slot': item_data['item_slot_type']}

            if item_event.get('sold_time_s') > 0:
                itemDetails['sold_time_s'] = item_event['sold_time_s']

            playerTimelineEvents.append(MatchPlayerTimelineEvent(
                match=match,
                player=player,
                timestamp=item_event['game_time_s'],
                type='item',
                details=itemDetails,
            ))

    def handleMatchPlayerTimelineAbilityEvent(self, player, match, item_event, item_data, playerTimelineEvents):
        if item_data:
            if match.date - int(time.time()) >= 1296000:
                playerTimelineEvents.append(MatchPlayerTimelineEvent(
                    match=match,
                    player=player,
                    timestamp=item_event['game_time_s'],
                    type='level',
                    details={'target': item_data['name']}
                ))

    def createMatchPlayerData(self, player, playerToTrack, match, matchMetadata, abandoned=None):
        if abandoned:
            return {
                'playerModel': playerToTrack,
                'match': match,
                'steam_id3': player['account_id'],
                'team': player.get('team'),
                'playerSlot': player.get('player_slot'),
                'abandoned': True,
                'abandonedTime': abandoned,
            }

        return {
            'playerModel': playerToTrack,
            'match': match,
            'steam_id3': player['account_id'],
            'team': str(player.get('team')),
            'playerSlot': player.get('player_slot'),
            'kills': player.get('kills', 0),
            'deaths': player.get('deaths', 0),
            'assists': player.get('assists', 0),
            'hero_deadlock_id': player.get('hero_id'),
            'level': player.get('level', 1),
            'items': {},
            'abilities': {},
            'souls': player.get('net_worth', 0),
            'soulsPerMin': 0,
            'lastHits': player.get('last_hits', 0),
            'denies': player.get('denies', 0),
            'party': player.get('party'),
            'lane': player.get('assigned_lane'),
            'laneCreeps': 0,
            'neutralCreeps': 0,
            'accuracy': 0,
            'heroCritPercent': 0,
            'soulsBreakdown': {},
            'heroDamage': 0,
            'objDamage': 0,
            'healing': 0,
            'win': player.get('team') == matchMetadata.get('winning_team'),
            'multis': None,
            'streaks': None,
            'medals': []
        }

    def createMatchPlayer(self, matchPlayersToCreate, data, multis, streakCounts, abandoned=None):
        if abandoned:
            mp = MatchPlayerModel(
                player=data['playerModel'],
                match=data['match'],
                steam_id3=data['steam_id3'],
                team=data['team'],
                playerSlot=data['playerSlot'],
                abandoned=True,
                abandonedTime=abandoned,
            )
        else:
            abilities = sorted(data['abilities'].items(), key=lambda x: (-len(x[1]), x[1]))
            mp = MatchPlayerModel(
                player=data['playerModel'],
                match=data['match'],
                steam_id3=data['steam_id3'],
                team=data['team'],
                playerSlot=data['playerSlot'],
                kills=data['kills'],
                deaths=data['deaths'],
                assists=data['assists'],
                hero_deadlock_id=data['hero_deadlock_id'],
                level=data['level'],
                items=data['items'],
                abilities=abilities,
                souls=data['souls'],
                soulsPerMin=data['soulsPerMin'],
                lastHits=data['lastHits'],
                denies=data['denies'],
                party=data['party'],
                lane=data['lane'],
                laneCreeps=data['laneCreeps'],
                neutralCreeps=data['neutralCreeps'],
                accuracy=data['accuracy'],
                heroCritPercent=data['heroCritPercent'],
                soulsBreakdown=data['soulsBreakdown'],
                heroDamage=data['heroDamage'],
                objDamage=data['objDamage'],
                healing=data['healing'],
                win=data['win'],
                multis=multis,
                streaks=streakCounts,
                medals=data['medals'],
            )
        matchPlayersToCreate.append(mp)
        return matchPlayersToCreate
