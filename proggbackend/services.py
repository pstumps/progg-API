import requests
from datetime import datetime
from django.conf import settings

import json

BASE_DIR = settings.BASE_DIR

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
        url = self.base_url + '/v2/players/' + str(account_id) + '/match-history'

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
        url = self.base_url + '/v2/hero-matchups-win-loss-stats'

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


class deadlockAPIDataService:
    def __init__(self):
        self.base_url = 'https://data.deadlock-api.com'

    def getActiveMatches(self):
        url = self.base_url + '/v1/active-matches'
        response = requests.get(url)
        return response.json()

    def getMatchMetadata(self, dl_match_id):
        url = self.base_url + '/v1/matches/' + str(dl_match_id) + '/metadata'

        # For Testing only
        with open(str(BASE_DIR) + '\\proggbackend\\response_1737591693017.json') as f:
            response = json.load(f)
        return response

        #response = requests.get(url)
        #return response.json()

    def getBigPatchDays(self):
        url = self.base_url + '/v1/big-patch-days'
        # response = requests.get(url)
        # print(response.json())
        # return response.json()
        # Temporary for testing
        return ['2024-12-06T20:05:10Z', '2024-11-21T23:21:49Z', '2024-11-07T21:31:34Z', '2024-10-24T19:39:08Z', '2024-10-10T20:24:45Z', '2024-09-26T21:17:58Z']

    def getLatestPatchUnixTimestamp(self):
        data = self.getBigPatchDays()
        dt = datetime.strptime(data[0], "%Y-%m-%dT%H:%M:%SZ")
        return int(dt.timestamp())

    def convertToUnixTimestamp(self, date):
        dt = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
        return int(dt.timestamp())


class deadlockAPIAssetsService:
    def __init__(self):
        self.base_url = 'https://assets.deadlock-api.com'

    def getHeroAssets(self):
        url = self.base_url + '/v1/heroes'
        response = requests.get(url)
        return response.json()

    def getItemAssets(self):
        url = self.base_url + '/v2/items'
        response = requests.get(url)
        return response.json()

    def getItemById(self, item_id, langauge=None, client_version=None):
        #url = self.base_url + '/v2/items/' + str(item_id)
        #response = requests.get(url)
        with open(BASE_DIR + 'proggbackend\\ItemData.json') as f:
            response = json.load(f)
        return response


    def getAbilityAssets(self):
        url = self.base_url + '/v1/abilities'
        response = requests.get(url)
        return response.json()

    def getBadgeAssets(self):
        url = self.base_url + '/v1/badges'
        response = requests.get(url)
        return response.json()

    def getItemsDict(self):
        with open(str(BASE_DIR) + '\\proggbackend\\ItemData.json') as f:
            response = json.load(f)
        return {item['id']: item for item in response}