import datetime
from django.db import transaction
from .Models.MatchesModel import MatchesModel
from .Models.MatchPlayerModel import MatchPlayerModel
from .Models.MatchPlayerTimeline import MatchPlayerTimelineEvent
from ..players.Models.PlayerModel import PlayerModel
from ..players.Models.PlayerHeroModel import PlayerHeroModel
from .Models.MatchTimeline import PvPEvent, ObjectiveEvent, MidbossEvent
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

    averageBadges['match_average_badge'] = int(badgesSum / len(averageBadges)) if averageBadges else 0
    return averageBadges


class proggAPIMatchesService:
    def __init__(self):
        self.DLAPIAnalytics = deadlockAPIAnalyticsService()
        self.DLAPIData = deadlockAPIDataService()
        self.DLAPIAssets = deadlockAPIAssetsService()
        self.DLItemsDict = self.DLAPIAssets.getItemsDict()

    @transaction.atomic
    def createNewMatchFromMetadata(self, matchMetadata):
        # self.deleteAllMatchesAndPlayersModels()
        # match id 32364484 players abandoned match
        matchMetadata = matchMetadata.get('match_info')
        if matchMetadata:
            dl_match_id = matchMetadata.get('match_id')

            if MatchesModel.objects.filter(deadlock_id=dl_match_id).exists():
                return MatchesModel.objects.get(deadlock_id=dl_match_id)

            print(f'dl match id: {dl_match_id}')

            averageBadges = calculateAverageBadgeFromMetadata(matchMetadata)
            match = MatchesModel.objects.create(
                deadlock_id=dl_match_id,
                date=datetime.datetime.fromtimestamp(matchMetadata.get('start_time'), datetime.timezone.utc) if matchMetadata.get('start_time') else None,
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
        match_event_details = {}
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

            playerToTrack = PlayerModel.objects.filter(steam_id3=player['account_id']).first()
            if not playerToTrack:
                playerToTrack = PlayerModel.objects.create(
                    steam_id3=player['account_id'],
                )
                print(f'created player: {playerToTrack.steam_id3}; name: {playerToTrack.name}')

            abilityLevels = {}
            createTimeline = False
            if match.date < datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7):
                createTimeline = playerToTrack.timelineTracking

            if player['account_id'] not in match_event_details:
                match_event_details[player['account_id']] = {
                    'hero_id': player['hero_id'],
                    'items': {},
                    'abilities': [],
                }

            if player.get('death_details'):
                self.processDeathDetails(player, player_details, streaks, lastKillTimes, multis, streakCounts,
                                         longestStreaks, match)

            if player.get('items'):
                for item_events in player.get('items'):
                    self.processItemEvents(player, item_events, match_event_details, abilityLevels, createTimeline,
                                           playerToTrack, match)

            sortedAbilities = sorted(abilityLevels.items(), key=lambda x: (-len(x[1]), x[1]))

            matchPlayer = self.createNewMatchPlayerFromMetadata(playerToTrack, match, player, matchMetadata)
            matchPlayer.items = match_event_details[player['account_id']].get('items', {})
            matchPlayer.abilities = [ability[0] for ability in sortedAbilities]
            matchPlayer.save()

        objectiveEvents, midbossEvents = self.processObjectivesAndMidbossEvents(match, matchMetadata)

        print(f'account ids: {match_event_details.keys()}')
        for account_id in match_event_details.keys():  # multis and streaks have same keys
            matchPlayer = MatchPlayerModel.objects.get(match=match, steam_id3=account_id)
            matchPlayer.multiKills = multis[account_id]
            matchPlayer.streaks = streakCounts[account_id]
            matchPlayer.save()

            # Will also update PlayerHeroModel
            player = matchPlayer.player
            player.updatePlayerStatsFromMatchPlayer(matchPlayer, multis, streakCounts, longestStreaks, objectiveEvents, midbossEvents)

        self.getPlayerMedals(match)

        return match_event_details

    def processDeathDetails(self, player, player_details, streaks, lastKillTimes, multis, streakCounts, longestStreaks,
                            match):
        for death_event in player['death_details']:
            slayer_slot = death_event.get('killer_player_slot')
            if not slayer_slot:
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

            if match.date < datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7):
                self.createMatchTimelinePvPEvent(match, slayer_info['hero_id'], player['hero_id'],
                                                 death_event['game_time_s'], player['team'])

    def processItemEvents(self, player, item_events, match_event_details, abilityLevels, createTimeline, playerToTrack,
                          match):

        item_data = self.DLItemsDict.get(item_events['item_id'])
        if item_data:
            if item_data.get('type') == 'ability':
                if item_data['name'] not in abilityLevels:
                    abilityLevels[item_data['name']] = []
                else:
                    abilityLevels[item_data['name']].append(item_events['game_time_s'])

                if createTimeline:
                    self.createMatchPlayerTimelineAbilityEvent(playerToTrack, match, item_events, item_data)

            elif item_data.get('type') == 'upgrade':
                playerItemsDictionary = match_event_details[player['account_id']]['items']
                if item_events['sold_time_s'] == 0 and item_events['upgrade_id'] == 0:
                    # Item was a part of final build
                    if item_data['item_slot_type'] not in playerItemsDictionary:
                        playerItemsDictionary[item_data['item_slot_type']] = []
                    if len(playerItemsDictionary[item_data['item_slot_type']]) >= 4:
                        if not playerItemsDictionary.get('flex'):
                            playerItemsDictionary['flex'] = []

                        playerItemsDictionary['flex'].append({
                            'item_id': item_events['item_id'],
                            'target': item_data['name'],
                            'type': item_data['item_slot_type']
                        })
                    else:
                        playerItemsDictionary[item_data['item_slot_type']].append({
                            'item_id': item_events['item_id'],
                            'target': item_data['name'],
                        })
                if createTimeline:
                    self.createMatchPlayerTimelineItemEvent(playerToTrack, match, item_events, item_data)

    def processObjectivesAndMidbossEvents(self, match, matchMetadata):
        objectiveEvents = []
        midbossEvents = []

        # Sketchy way of getting opposite teams. TODO: Need to fix this
        oppositeTeams = {'k_ECitadelLobbyTeam_Team0': 'k_ECitadelLobbyTeam_Team1',
                         'k_ECitadelLobbyTeam_Team1': 'k_ECitadelLobbyTeam_Team0'}

        if matchMetadata.get('objectives'):
            for obj in matchMetadata['objectives']:
                objectiveEvents.append(self.createMatchTimelineObjectiveEvent(match=match,
                                                                              target=obj['team_objective_id'],
                                                                              timestamp=obj['destroyed_time_s'],
                                                                              team=oppositeTeams[obj['team']]))
        if matchMetadata.get('mid_boss'):
            for midboss in matchMetadata['mid_boss']:
                midbossEvents.append(self.createMatchTimelineMidbossEvent(match=match,
                                                                          slayer=midboss['team_killed'],
                                                                          team=midboss['team_claimed'],
                                                                          timestamp=midboss['destroyed_time_s']))

        return objectiveEvents, midbossEvents

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

    def getPlayerMedals(self, match):
        top_kills_player = MatchPlayerModel.objects.filter(match=match).order_by('-kills').first()
        top_hero_damage_player = MatchPlayerModel.objects.filter(match=match).order_by('-heroDamage').first()
        top_souls_player = MatchPlayerModel.objects.filter(match=match).order_by('-souls').first()
        top_assists_player = MatchPlayerModel.objects.filter(match=match).order_by('-assists').first()
        top_obj_damage_player = MatchPlayerModel.objects.filter(match=match).order_by('-objDamage').first()
        top_healing_player = MatchPlayerModel.objects.filter(match=match).order_by('-healing').first()

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

    # Testing purposes only
    def deleteAllMatchesAndPlayersModels(self):
        MatchesModel.objects.all().delete()
        MatchPlayerModel.objects.all().delete()
        MatchPlayerTimelineEvent.objects.all().delete()
        PlayerModel.objects.all().delete()
        PlayerHeroModel.objects.all().delete()
        PvPEvent.objects.all().delete()
        ObjectiveEvent.objects.all().delete()
        MidbossEvent.objects.all().delete()