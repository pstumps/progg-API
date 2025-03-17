import datetime, requests, os, environ, json
from django.conf import settings

BASE_DIR = settings.BASE_DIR
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
DL_API_KEY = env('DL_API_KEY')

class deadlockAPIDataService:
    def __init__(self):
        self.base_url = 'https://api.deadlock-api.com'
        self.dl_api_key = DL_API_KEY

    def getActiveMatches(self):
        print('Getting active matches from data.deadlock-api...')
        url = self.base_url + '/v1/active-matches'
        response = requests.get(url)
        return response.json()

    def getMatchMetadata(self, dl_match_id, api_key=None):
        print(f'Getting match metadata for match {dl_match_id} from data.deadlock-api...')
        url = self.base_url + '/v1/matches/' + str(dl_match_id) + '/metadata'

        params = {
            'match_id': dl_match_id,
            'api_key': api_key if api_key else self.dl_api_key
        }
        '''
        #For Testing only
        with open(str(BASE_DIR) + '\\proggbackend\\Response_newmetadata.json') as f:
            response = json.load(f)
        return response
        '''
        params = {key: value for key, value in params.items() if value is not None}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f'Request error: {e}')
            return None
        except ValueError as e:
            print(f'json error: {e}')
            return None

        return data


    def getMatchMetadataTest(self, dl_match_id, api_key=None):
        print(f'Getting match metadata for match {dl_match_id} from data.deadlock-api...')
        with open(str(BASE_DIR) + '\\proggbackend\\response_1737591693017.json') as f:
            response = json.load(f)
        return response

    def getBigPatchDays(self):
        print('Getting big patch days from data.deadlock-api...')
        url = self.base_url + '/v1/big-patch-days'
        response = requests.get(url)
        # print(response.json())
        return response.json()
        # Temporary for testing
        #return ['2025-02-25T21:51:13Z', '2024-12-06T20:05:10Z', '2024-11-21T23:21:49Z', '2024-11-07T21:31:34Z', '2024-10-24T19:39:08Z', '2024-10-10T20:24:45Z', '2024-09-26T21:17:58Z']

    def getLatestPatchUnixTimestamp(self):
        data = self.getBigPatchDays()
        dt = datetime.datetime.strptime(data[0], "%Y-%m-%dT%H:%M:%SZ")
        return int(dt.timestamp())

    def convertToUnixTimestamp(self, date):
        dt = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
        return int(dt.timestamp())