import requests


class deadlockAPIAnalyticsService:
    def __init__(self):
        self.base_url = 'https://analytics.deadlock-api.com'

    def getHeroesWinLossStats(self):
        url = self.base_url + '/v2/hero-win-loss-stats'
        response = requests.get(url)
        return response.json()


class deadlockAPIDataService:
    def __init__(self):
        self.base_url = 'https://data.deadlock-api.com'

    def getActiveMatches(self):
        url = self.base_url + '/v1/active-matches'
        response = requests.get(url)
        return response.json()
