import requests
from django.conf import settings

BASE_DIR = settings.BASE_DIR

class deadlockAPIAnalyticsService:
    def __init__(self):
        self.base_url = 'https://api.deadlock-api.com'

    def getHeroesWinLossStats(self, mid_badge_level=None, max_badge_level=None, min_hero_matches_per_player=None,
                              max_hero_matches_per_player=None, min_unix_timestamp=None, max_unix_timestamp=None,
                              match_mode=None, region=None):
        print('Getting hero win/loss from api.deadlock-api...')
        url = self.base_url + '/v1/analytics/hero-stats'

        params = {
            'mid_badge_level': mid_badge_level,
            'max_badge_level': max_badge_level,
            'min_hero_matches_per_player': min_hero_matches_per_player,
            'max_hero_matches_per_player': max_hero_matches_per_player,
            'min_unix_timestamp': min_unix_timestamp,
            'max_unix_timestamp': max_unix_timestamp,
            'match_mode': match_mode,
            'region': region
        }

        params = {key: value for key, value in params.items() if value is not None}
        response = requests.get(url, params=params)
        return response.json()

    def getCombinedHeroesWinLossStats(self, comb_size=None, include_hero_ids=None, exclude_hero_ids=None,
                                      min_total_matches=None, sorted_by=None, limit=None, min_badge_level=None,
                                      max_badge_level=None, min_unix_timestamp=None, max_unix_timestamp=None,
                                      match_mode=None, region=None):
        print('Getting combined heroes win/loss stats from analytics.deadlock-api...')
        url = self.base_url + '/v1/analytics/hero-comb-win-loss-stats'

        params = {
            'comb_size': comb_size,
            'include_hero_ids': include_hero_ids,
            'exclude_hero_ids': exclude_hero_ids,
            'min_total_matches': min_total_matches,
            'sorted_by': sorted_by,
            'limit': limit,
            'min_badge_level': min_badge_level,
            'max_badge_level': max_badge_level,
            'min_unix_timestamp': min_unix_timestamp,
            'max_unix_timestamp': max_unix_timestamp,
            'match_mode': match_mode,
            'region': region
        }

        params = {key: value for key, value in params.items() if value is not None}

        # Temporary json file loading for testing
        #if min_unix_timestamp == 1732260109 and max_unix_timestamp == 1733544310:
        #    with open('C:\\Users\\patrick.x.stumps\\Documents\\proggbackend\\proggbackend\\response_1736531551242.json') as f:
        #        response = json.load(f)
        #else:
        #    with open('C:\\Users\\patrick.x.stumps\\Documents\\proggbackend\\proggbackend\\response_1736269436806.json') as f:
        #        response = json.load(f)
        #if include_hero_ids:
        #    response = [entry for entry in response if entry['hero_ids'][0] == include_hero_ids]
        #return response

        response = requests.get(url, params=params)
        return response.json()

    # def getHeroItemWinLossStats(self, hero_id=None, item_id=None, min_badge_level=None, max_badge_level=None,
    #                            min_unix_timestamp=None, max_unix_timestamp=None, match_mode=None, region=None):
    # WIP

    def getPlayerMatchHistory(self, account_id, has_metadata=False, min_unix_timestamp=None, max_unix_timestamp=None,
                              min_match_id=None, max_match_id=None, min_duration_s=None, max_duration_s=None,
                              match_mode=None):
        url = self.base_url + '/v1/players/' + str(account_id) + '/match-history'
        print('Getting player match history from analytics.deadlock-api...')

        params = {'account_id': account_id,
                    'has_metadata': has_metadata,
                    'min_unix_timestamp': min_unix_timestamp,
                    'max_unix_timestamp': max_unix_timestamp,
                    'min_match_id': min_match_id,
                    'max_match_id': max_match_id,
                    'min_duration_s': min_duration_s,
                    'max_duration_s': max_duration_s,
                    'match_mode': match_mode}

        params = {key: value for key, value in params.items() if value is not None}

        #with open(
        #        'C:\\Users\\patrick.x.stumps\\Documents\\proggbackend\\proggbackend\\response_1736890575828.json') as f:
        #    response = json.load(f)
        response = requests.get(url, params=params)
        return response.json()

    def getMatchupStats(self, min_badge_level=None, max_badge_level=None, min_unix_timestamp=None, max_unix_timestamp=None,
                        match_mode=None, region=None):
        url = self.base_url + '/v1/analytics/hero-counter-stats'
        print('Getting hero matchup stats from analytics.deadlock-api...')

        params = {
            'min_badge_level': min_badge_level,
            'max_badge_level': max_badge_level,
            'min_unix_timestamp': min_unix_timestamp,
            'max_unix_timestamp': max_unix_timestamp,
            'match_mode': match_mode,
            'region': region
        }

        params = {key: value for key, value in params.items() if value is not None}

        # Temporary json file loading for testing
        #if min_unix_timestamp == 1732260109 and max_unix_timestamp == 1733544310:
        #    with open('C:\\Users\\patrick.x.stumps\\Documents\\proggbackend\\proggbackend\\response_1736885677655.json') as f:
        #        response = json.load(f)
        #else:
        #    with open('C:\\Users\\patrick.x.stumps\\Documents\\proggbackend\\proggbackend\\response_1736885638503.json') as f:
        #        response = json.load(f)

        response = requests.get(url, params=params)
        return response.json()