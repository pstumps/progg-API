import requests
from django.conf import settings

BASE_DIR = settings.BASE_DIR

class deadlockAPIDataService:
    def __init__(self):
        self.base_url = 'https://data.deadlock-api.com'

    def getActiveMatches(self):
        url = self.base_url + '/v1/active-matches'
        response = requests.get(url)
        return response.json()

    def getMatchMetadata(self, dl_match_id):
        url = self.base_url + '/v1/matches/' + str(dl_match_id) + '/metadata'

        #For Testing only
        # with open(str(BASE_DIR) + '\\proggbackend\\response_1737591693017.json') as f:
        #    response = json.load(f)
        #return response

        response = requests.get(url)
        return response.json()

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