import requests
from datetime import datetime

import json

class deadlockAPIAnalyticsService:
    def __init__(self):
        self.base_url = 'https://analytics.deadlock-api.com'

    def getHeroesWinLossStats(self, mid_badge_level=None, max_badge_level=None, min_hero_matches_per_player=None,
                              max_hero_matches_per_player=None, min_unix_timestamp=None, max_unix_timestamp=None,
                              match_mode=None, region=None):
        url = self.base_url + '/v2/hero-win-loss-stats'

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
        url = self.base_url + '/v2/combined-heroes-win-loss-stats'

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
        with open('C:\\Users\\patrick.x.stumps\\Documents\\proggbackend\\proggbackend\\response_1736269436806.json') as f:
            response = json.load(f)
        if include_hero_ids:
            response = [entry for entry in response if entry['hero_ids'][0] == include_hero_ids]

        return response

        # response = requests.get(url, params=params)
        # return response.json()


class deadlockAPIDataService:
    def __init__(self):
        self.base_url = 'https://data.deadlock-api.com'

    def getActiveMatches(self):
        url = self.base_url + '/v1/active-matches'
        response = requests.get(url)
        return response.json()

    def getBigPatchDays(self):
        url = self.base_url + '/v1/big-patch-days'
        # response = requests.get(url)
        # print(response.json())
        # return response.json()
        # Temporary for testing
        return ['2024-12-06T20:05:10Z']

    def getLatestPatchUnixTimestamp(self):
        data = self.getBigPatchDays()
        dt = datetime.strptime(data[0], "%Y-%m-%dT%H:%M:%SZ")
        return int(dt.timestamp())


