import os
import json
from django.test import TestCase
from django.conf import settings
from unittest.mock import patch, MagicMock

from apps.matches.services.MetadataServices import MetadataServices
from apps.players.Models.PlayerModel import PlayerModel
from apps.matches.Models.MatchPlayerModel import MatchPlayerModel

from proggbackend.services.DeadlockAPIAssets import deadlockAPIAssetsService

class MetadataServicesPlayerDataTestCase(TestCase):

    def setUp(self):
        # Update path to actual location
        json_path = os.path.join(settings.BASE_DIR, 'proggbackend', 'Response_newmetadata.json')
        with open(json_path, 'r') as file:
            self.metadata_json = json.load(file)

        assets = deadlockAPIAssetsService()
        dlItems = assets.getItemsDict()

        self.metadata = self.metadata_json['match_info']
        self.service = MetadataServices(dlItems)
        self.match = MagicMock()
        self.expected_player_model = MagicMock()

        # Example expected data for a player (steam_id3: 1284146610)
        self.expected_player = {
            'steam_id3': 1284146610,
            'party': 0,
            'playerSlot': 5,
            'hero_deadlock_id': 4,
            'team': '0',
            'lane': 4,
            'kills': 7,
            'deaths': 4,
            'assists': 16,
            'souls': 36945,
            'soulsBreakdown': {
                "hero": 4126,
                "lane_creeps": 21249,
                "neutrals": 3741,
                "objectives": 3503,
                "crates": 0,
                "assists": 289,
                "denies": 1526,
                "other": 2530
            },
            'soulsPerMin': 1075.02,
            'level': 31,
            'accuracy': 0.6272,
            'heroCritPercent': 0.1105,
            'heroDamage': 24094,
            'objDamage': 7700,
            'healing': 26245,
            'laneCreeps': 100,
            'neutralCreeps': 15,
            'lastHits': 188,
            'denies': 7,
            'items': {
                "vitality": [1710079648, 3970837787, 876563814, 4139877411],
                "spirit": [1998374645, 754480263, 787198704, 7409189],
                "weapon": [3977876567, 3270001687],
                "flex": [3005970438, 865846625],
                "percentages": [25.0, 62.5, 62.5]
            },
            'abilities': {
                "Life Drain": [470, 627, 822],
                "Malice": [471, 1145, 1423],
                "Essence Bomb": [59, 222],
                "Soul Exchange": [335, 1599]
            },
            'multis': [1, 0, 0, 0, 0, 0],
            'streaks': [2, 1, 0, 0, 0, 0, 4],
            'medals': ["2nd", "healing"],
            'longestStreak': 0
        }
        self.expected_player_items = self.metadata['players'][0]['items']
    def test_createMatchPlayerData(self):
        """Test creating basic match player data"""
        # Get player data for the specific steam_id
        player_data = None
        for player in self.metadata['players']:
            if player['account_id'] == self.expected_player['steam_id3']:
                player_data = player
                break

        self.assertIsNotNone(player_data, "Test player not found in metadata")

        # Call the createMatchPlayerData method
        result = self.service.createMatchPlayerData(player_data, self.expected_player_model, self.match, self.metadata)

        # Verify basic player info
        self.assertEqual(result['steam_id3'], self.expected_player['steam_id3'])
        self.assertEqual(result['playerSlot'], self.expected_player['playerSlot'])
        self.assertEqual(result['hero_deadlock_id'], self.expected_player['hero_deadlock_id'])
        self.assertEqual(result['team'], self.expected_player['team'])
        self.assertEqual(result['kills'], self.expected_player['kills'])
        self.assertEqual(result['deaths'], self.expected_player['deaths'])
        self.assertEqual(result['assists'], self.expected_player['assists'])

    def test_computePlayerMetadata(self):
        """Test computing player metadata like souls, damage, etc."""
        player_data = None
        for player in self.metadata['players']:
            if player['account_id'] == self.expected_player['steam_id3']:
                player_data = player
                break

        # Create initial player data dict
        player_dict = self.service.createMatchPlayerData(player_data, self.expected_player_model, self.match, self.metadata)

        # Call computePlayerMetadata
        result = self.service.computePlayerMetadata(self.metadata, self.metadata['players'][0])

        # Verify computed metadata
        self.assertEqual(result['souls'], self.expected_player['souls'])
        self.assertEqual(result['soulsBreakdown'], self.expected_player['soulsBreakdown'])
        self.assertAlmostEqual(result['soulsPerMin'], self.expected_player['soulsPerMin'], places=1)
        self.assertEqual(result['laneCreeps'], self.expected_player['laneCreeps'])
        self.assertEqual(result['neutralCreeps'], self.expected_player['neutralCreeps'])
        self.assertAlmostEqual(result['accuracy'], self.expected_player['accuracy'], places=3)
        self.assertAlmostEqual(result['heroCritPercent'], self.expected_player['heroCritPercent'], places=3)
        self.assertEqual(result['heroDamage'], self.expected_player['heroDamage'])
        self.assertEqual(result['objDamage'], self.expected_player['objDamage'])
        self.assertEqual(result['healing'], self.expected_player['healing'])

    def test_processItemEvents(self):
        """Test processing item events to generate items and abilities"""
        player_data = None
        for player in self.metadata['players']:
            if player['account_id'] == self.expected_player['steam_id3']:
                player_data = player
                break

        # Call processItemEvents
        player_data[self.expected_player['steam_id3']] = {'abilities': {}, 'items': {}, 'playerModel': self.expected_player_model}
        result = self.service.processItemEvents(self.expected_player_items, player_data, self.expected_player['steam_id3'], [])

        # Verify items and abilities
        self.assertEqual(result[self.expected_player['steam_id3']]['items'], self.expected_player['items'])
        self.assertEqual(result[self.expected_player['steam_id3']]['abilities'], self.expected_player['abilities'])

    '''
    def test_processDeathDetails(self):
        """Test processing death details to generate streaks and multis"""
        player_data = None
        for player in self.metadata_json['players']:
            if player['account_id'] == self.expected_player['steam_id3']:
                player_data = player
                break

        # Create initial player data dict
        player_dict = {"steam_id3": self.expected_player['steam_id3']}

        # Call processDeathDetails
        result = self.service.processDeathDetails(player_dict, player_data)

        # Verify streaks and multis
        self.assertEqual(result['streaks'], self.expected_player['streaks'])
        self.assertEqual(result['multis'], self.expected_player['multis'])
        self.assertEqual(result['longestStreak'], self.expected_player['longestStreak'])
    

    def test_getMedals(self):
        """Test getting medals for a player"""
        # Create mock match player objects for all players
        mock_players = []
        for player in self.metadata_json['players']:
            mock_player = MagicMock()
            mock_player.steam_id3 = player['account_id']
            mock_player.team = player['team']
            mock_player.kills = player['kills']
            mock_player.deaths = player['deaths']
            mock_player.assists = player['assists']
            mock_player.heroDamage = 20000  # Sample value
            mock_player.objDamage = 5000  # Sample value
            mock_player.healing = 0  # Set appropriate values for testing
            mock_players.append(mock_player)

            # Set healing for our test player
            if player['account_id'] == self.expected_player['steam_id3']:
                mock_player.healing = self.expected_player['healing']

        # Call getMedals
        result = self.service.getMedals(mock_players)

        # Find our test player in the results
        test_player_medals = None
        for player in result:
            if player.steam_id3 == self.expected_player['steam_id3']:
                test_player_medals = player.medals
                break

        # Verify medals (excluding ranking which is added by rankMatchPlayers)
        self.assertIn("healing", test_player_medals)

    @patch('apps.matches.Models.MatchesModel.MatchesModel')
    def test_rankMatchPlayers(self, mock_match_model):
        """Test ranking match players"""
        mock_match = MagicMock()
        mock_match.victor = "0"  # Set the winning team

        # Create mock players
        mock_players = []
        for idx, player_data in enumerate(self.metadata_json['players']):
            mock_player = MagicMock()
            mock_player.steam_id3 = player_data['account_id']
            mock_player.kills = player_data['kills']
            mock_player.deaths = player_data['deaths']
            mock_player.assists = player_data['assists']
            mock_player.souls = 30000 + idx * 1000  # Sample values
            mock_player.heroDamage = 20000 + idx * 1000
            mock_player.objDamage = 5000
            mock_player.healing = 1000
            mock_player.lastHits = 150
            mock_player.denies = 5
            mock_player.accuracy = 0.5
            mock_player.team = player_data['team']
            mock_player.medals = []
            mock_players.append(mock_player)

        # Call rankMatchPlayers
        mock_match_model().rankMatchPlayers(mock_match, mock_players)

        # Verify all players have rankings in their medals
        for player in mock_players:
            self.assertTrue(len(player.medals) > 0)
            # Check if first medal is a ranking (MVP, SVP, or ordinal position)
            first_medal = player.medals[0]
            valid_first_medals = ["MVP", "SVP"] + [f"{i}st" for i in range(1, 21)] + \
                                 [f"{i}nd" for i in range(2, 21)] + \
                                 [f"{i}rd" for i in range(3, 21)] + \
                                 [f"{i}th" for i in range(4, 21)]
            self.assertIn(first_medal, valid_first_medals,
                          f"First medal '{first_medal}' is not a valid ranking")
    

    def test_end_to_end_player_creation(self):
        """Test the full player creation pipeline from metadata"""
        # Create a mock match
        mock_match = MagicMock()
        mock_match.victor = "0"  # Set the winning team

        # Call the service method to create all players
        mock_players = self.service.createAllMatchPlayers(mock_match)

        # Find our test player
        test_player = None
        for player in mock_players:
            if player.steam_id3 == self.expected_player['steam_id3']:
                test_player = player
                break

        self.assertIsNotNone(test_player, "Test player was not created")

        # Verify all expected fields
        self.assertEqual(test_player.steam_id3, self.expected_player['steam_id3'])
        self.assertEqual(test_player.playerSlot, self.expected_player['playerSlot'])
        self.assertEqual(test_player.hero_deadlock_id, self.expected_player['hero_deadlock_id'])
        self.assertEqual(test_player.team, self.expected_player['team'])
        self.assertEqual(test_player.kills, self.expected_player['kills'])
        self.assertEqual(test_player.deaths, self.expected_player['deaths'])
        self.assertEqual(test_player.assists, self.expected_player['assists'])
        self.assertEqual(test_player.souls, self.expected_player['souls'])
        self.assertEqual(test_player.soulsBreakdown, self.expected_player['soulsBreakdown'])
        self.assertAlmostEqual(test_player.soulsPerMin, self.expected_player['soulsPerMin'], places=1)
        self.assertEqual(test_player.items, self.expected_player['items'])
        self.assertEqual(test_player.abilities, self.expected_player['abilities'])
        self.assertEqual(test_player.multis, self.expected_player['multis'])
        self.assertEqual(test_player.streaks, self.expected_player['streaks'])

        # Check for medals (at least some of them)
        for medal in self.expected_player['medals']:
            if medal != self.expected_player['medals'][0]:  # Skip checking ranking position
                self.assertIn(medal, test_player.medals)
    '''