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
from proggbackend.services.SteamWebAPI import SteamWebAPIService


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

            existingMatch = MatchesModel.objects.filter(deadlock_id=dl_match_id).first()
            if existingMatch:
                return existingMatch

            print(f'dl match id: {dl_match_id}')

            averageBadges = calculateAverageBadgeFromMetadata(matchMetadata)
            match = MatchesModel.objects.create(
                deadlock_id=dl_match_id,
                date=matchMetadata.get('start_time') if matchMetadata.get('start_time') else None,
                averageRank=averageBadges if averageBadges else None,
                gameMode=matchMetadata.get('game_mode'),
                matchMode=matchMetadata.get('match_mode'),
                length=matchMetadata.get('duration_s'),
                victor=matchMetadata.get('winning_team')
            )

            self.parseMatchEventsFromMetadata(match, matchMetadata)

            match.calculateTeamStats()
            match.save()

            return match
        return None

    @transaction.atomic
    def parseMatchEventsFromMetadata(self, match, matchMetadata):
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

        all_account_ids = [p['account_id'] for p in matchMetadata['players']]
        existing_players = PlayerModel.objects.in_bulk(all_account_ids, field_name='steam_id3')
        players_to_create = []
        steamService = SteamWebAPIService()
        for acct_id in all_account_ids:
            if acct_id not in existing_players:
                players_to_create.append(PlayerModel(steam_id3=acct_id))
        PlayerModel.objects.bulk_create(players_to_create)
        # for p in PlayerModel.objects.filter(steam_id3__in=all_account_ids):
        #    p.save()
        #    all_players[p.steam_id3] = p
        all_players = {p.steam_id3: p for p in PlayerModel.objects.filter(steam_id3__in=all_account_ids)}

        for player in matchMetadata['players']:
            account_id = player['account_id']
            playerToTrack = all_players[account_id]

            if account_id not in matchPlayerData:
                matchPlayerData[account_id] = self.createMatchPlayerData(player, playerToTrack, match, matchMetadata)

            if player.get('death_details'):
                self.processDeathDetails(player, player_details, streaks, lastKillTimes, multis, streakCounts,
                                         longestStreaks, matchPlayerData[account_id]['match'], pvpEvents)

            if player.get('items'):
                for item_events in player.get('items'):
                    self.processItemEvents(item_events, matchPlayerData, account_id, playerEvents)

            if player.get('stats'):
                for stat in player.get('stats'):
                    playerStatsGraphs.append(MatchPlayerGraph(
                        match=match,
                        steam_id3=account_id,
                        timestamp=stat['time_stamp_s'],
                        net_worth=stat.get('net_worth', 0),
                        player_damage=stat.get('player_damage', 0),
                        boss_damage=stat.get('boss_damage', 0),
                        player_healing=stat.get('player_healing', 0)
                    ))

            endStatsData = self.computePlayerMetadata(matchMetadata, player)
            matchPlayerData[account_id].update(endStatsData)

        PvPEvent.objects.bulk_create(pvpEvents)

        objectiveEvents, midbossEvents = self.processObjectivesAndMidbossEvents(match, matchMetadata)
        ObjectiveEvent.objects.bulk_create(objectiveEvents)
        MidbossEvent.objects.bulk_create(midbossEvents)
        MatchPlayerTimelineEvent.objects.bulk_create(playerEvents)

        print(f'account ids: {matchPlayerData.keys()}')
        matchPlayersToCreate = []
        for account_id, data in matchPlayerData.items():
            matchPlayersToCreate = self.createMatchPlayer(matchPlayersToCreate, data, multis.get(account_id), streakCounts.get(account_id))
            # Will also update PlayerHeroModel
            player = data['playerModel']

            # Below line is commmented out for testing only

            player.updatePlayerStatsFromMatchPlayer(data['team'],
                                                    multis.get(account_id),
                                                    streakCounts.get(account_id),
                                                    longestStreaks.get(account_id, 0),
                                                    objectiveEvents,
                                                    midbossEvents,
                                                    data['match'])

            player.updatePlayerHeroStatsFromMatchPlayer(data, longestStreaks.get(account_id, 0))

            player.updatePlayerRecords(data['hero_deadlock_id'], data['kills'], data['deaths'], data['assists'],
                                       data['souls'], data['heroDamage'], data['objDamage'], data['healing'])

            player.save()

        MatchPlayerGraph.objects.bulk_create(playerStatsGraphs)
        MatchPlayerModel.objects.bulk_create(matchPlayersToCreate)

        if matchPlayersToCreate:
            self.getMedals(matchPlayersToCreate)

            MatchPlayerModel.objects.bulk_update(matchPlayersToCreate, ['medals'])

        return matchPlayerData

    def createMatchPlayerData(self, player, playerToTrack, match, matchMetadata):

        return {
            'playerModel': playerToTrack,
            'match': match,
            'steam_id3': player['account_id'],
            'team': player.get('team'),
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
            'multis': [0] * 6,
            'streaks': [0] * 8,
            'medals': []
        }

    def createMatchPlayer(self, matchPlayersToCreate, data, multis, streakCounts):
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

    def processDeathDetails(self, player, player_details, streaks, lastKillTimes, multis, streakCounts, longestStreaks,
                            match, pvpEvents):
        for death_event in player['death_details']:
            slayer_slot = death_event.get('killer_player_slot')
            if slayer_slot is None:
                continue

            if slayer_slot not in player_details:
                continue

            slayer_info = player_details[slayer_slot]
            slayer_account_id = slayer_info['account_id']

            # Kill streak tracking
            if slayer_account_id not in streaks:
                streaks[slayer_account_id] = 0
            streaks[slayer_account_id] += 1
            streaks[player['account_id']] = 0

            if streaks[slayer_account_id] > longestStreaks.get(slayer_account_id, 0):
                longestStreaks[slayer_account_id] = streaks[slayer_account_id]

            if 3 <= streaks[slayer_account_id] <= 8:
                streakCounts[slayer_account_id][streaks[slayer_account_id] - 3] += 1
            elif streaks[slayer_account_id] > 8:
                streakCounts[slayer_account_id][7] += 1

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
                multis[slayer_account_id][min(multiKillCount, 7) - 2] += 1

            if match.date < int(time.time()) - 604800:
                pvpEvents.append(
                    PvPEvent(
                        match=match,
                        timestamp=death_event['game_time_s'],
                        team=player['team'],
                        slayer_hero_id=slayer_info['hero_id'],
                        victim_hero_id=player['hero_id']
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

                    playerItemsDictionary['flex'].append({
                        'target': item_data['name'],
                        'type': item_data['item_slot_type']
                    })
                else:
                    playerItemsDictionary[item_data['item_slot_type']].append(item_data['name'])
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

    def computePlayerMetadata(self, matchMetadata, playerMetadata):
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

        if playerSouls > 0:
            soulsBreakdown = {
                key: getGold(end_stats.get('gold_sources', []), idx, incOrbs)
                for key, (idx, incOrbs) in goldMapping.items()
            }
        else:
            soulsBreakdown = {k: 0 for k in goldMapping.keys()}

        return {
            'souls': playerSouls,
            'soulsPerMin': round(playerSouls / match_length, 2),
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

    @transaction.atomic
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
            playerTimelineEvents.append(MatchPlayerTimelineEvent(
                match=match,
                player=player,
                timestamp=item_event['game_time_s'],
                type='level',
                details={'target': item_data['name']}
            ))


    '''
    def getPlayerMedals(self, match):
        players = list(MatchPlayerModel.objects.filter(match=match))
        top_kills_player = max(players, key=lambda x: x.kills) if players else None
        top_hero_damage_player = max(players, key=lambda x: x.heroDamage) if players else None
        top_souls_player = max(players, key=lambda x: x.souls) if players else None
        top_assists_player = max(players, key=lambda x: x.assists) if players else None
        top_obj_damage_player = max(players, key=lambda x: x.objDamage) if players else None
        top_healing_player = max(players, key=lambda x: x.healing) if players else None

        medals_dict = {}

        def add_medal(player, medal):
            if player:
                if player.match_player_id not in medals_dict:
                    medals_dict[player.match_player_id] = {'player': player, 'medals': []}
                medals_dict[player.match_player_id]['medals'].append(medal)

        add_medal(top_kills_player, 'slays')
        add_medal(top_hero_damage_player, 'heroDmg')
        add_medal(top_souls_player, 'souls')
        add_medal(top_assists_player, 'assists')
        add_medal(top_obj_damage_player, 'objDmg')
        add_medal(top_healing_player, 'healing')

        for player_data in medals_dict.values():
            player = player_data['player']
            medals = player_data['medals']
            if not player.medals:
                player.medals = medals
            else:
                existing_medals = player.medals
                existing_medals.extend(medals)
                player.medals = existing_medals
            player.save()
    '''

    '''
    @transaction.atomic
    def createNewMatchPlayerFromMetadata(self, playerModel, match, playerMetadata, matchMetaData):
        def getGold(goldSources, index, includeOrbs=True):
            try:
                source = goldSources[index]
            except (IndexError, TypeError):
                return 0
            gold = source.get('gold', 0)
            if includeOrbs:
                gold += source.get('gold_orbs', 0)
            return gold

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

        endStats = playerMetadata['stats'][-1]
        playerSouls = endStats.get('net_worth')
        matchPlayer = MatchPlayerModel.objects.create(
            player=playerModel,
            match=match,
            steam_id3=playerMetadata.get('account_id'),
            team=playerMetadata.get('team'),
            playerSlot=playerMetadata.get('player_slot'),
            kills=playerMetadata.get('kills'),
            deaths=playerMetadata.get('deaths'),
            assists=playerMetadata.get('assists'),
            hero_deadlock_id=playerMetadata.get('hero_id'),
            level=playerMetadata.get('level'),
            souls=playerSouls,
            soulsPerMin=round(playerSouls / match.length, 2),
            lastHits=playerMetadata.get('last_hits'),
            denies=playerMetadata.get('denies'),
            party=playerMetadata.get('party'),
            lane=playerMetadata.get('assigned_lane'),
            laneCreeps=endStats.get('creep_kills'),
            neutralCreeps=endStats.get('neutral_kills'),
            accuracy=round(endStats.get('shots_hit') / (endStats.get('shots_hit') + endStats.get('shots_missed')), 4) if (endStats.get('shots_hit') + endStats.get('shots_missed')) > 0 else 0,
            heroCritPercent=round(endStats.get('hero_bullets_hit_crit') / endStats.get('hero_bullets_hit'), 4) if endStats.get('hero_bullets_hit') > 0 else 0,
            # dictionary of the key in goldMapping to the value returned by getGold function
            soulsBreakdown= {key: round(getGold(endStats.get('gold_sources'), index, includeOrbs) / playerSouls, 1)  if playerSouls > 0 else 0 for key, (index, includeOrbs) in goldMapping.items()},
            heroDamage=endStats.get('player_damage'),
            objDamage=endStats.get('boss_damage'),
            healing=endStats.get('player_healing'),
            win=playerMetadata.get('team') == matchMetaData.get('winning_team'),
        )
        return matchPlayer
    '''
