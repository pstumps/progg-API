import requests, logging
from django.conf import settings
logger = logging.getLogger(__name__)
API_KEY = settings.SOCIAL_AUTH_STEAM_API_KEY

class SteamWebAPIService:
    def __init__(self):
        self.apiKey = API_KEY
        self.ISteamUserBaseURL = 'https://api.steampowered.com/ISteamUser'
        self.IPlayerServiceBaseURL = 'https://api.steampowered.com/IPlayerService'

    def convertSteamID3ToSteamID64(self, steam_id3):
        # Get 64 bit steamID from steamID3
        steamid64ident = 76561197960265728
        commID = int(steam_id3) + steamid64ident
        return commID

    def getPlayerSummaries(self, steam_id3):
        try:
            steamid64 = self.convertSteamID3ToSteamID64(steam_id3)
            response = requests.get(
                f'{self.ISteamUserBaseURL}/GetPlayerSummaries/v0002/?key={self.apiKey}&steamids={steamid64}&format=json'
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.JSONDecodeError as e:
            logger.error(f"Steam API returned invalid JSON: {str(e)}")
            return {"response": {"players": []}}
        except requests.exceptions.RequestException as e:
            logger.error(f"Steam API request failed: {str(e)}")
            return {"response": {"players": []}}

    '''
    def getPlayerSummaries(self, steam_id3):
        print('Getting player summaries from Steam web API...')
        steamid64 = self.convertSteamID3ToSteamID64(steam_id3)
        url = f'{self.ISteamUserBaseURL}/GetPlayerSummaries/v0002/?key={self.apiKey}&steamids={steamid64}&format=json'
        response = requests.get(url)
        return response.json()
    '''

    def getPlayerName(self, steam_id3):
        print('Getting player name from Steam web API...')
        try:
            steamid64 = self.convertSteamID3ToSteamID64(steam_id3)
            url = f'{self.ISteamUserBaseURL}/GetPlayerSummaries/v0002/?key={self.apiKey}&steamids={steamid64}&format=json'
            response = requests.get(url)
            return response.json()['response']['players'][0]['personaname']
        except requests.exceptions.JSONDecodeError as e:
            logger.error(f"Steam API returned invalid JSON: {str(e)}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Steam API request failed: {str(e)}")
            return None

    def getOwnedGames(self, steam_id3):
        print('Getting player games from Steam web API...')
        try:
            steamid64 = self.convertSteamID3ToSteamID64(steam_id3)
            url = f'{self.IPlayerServiceBaseURL}/GetOwnedGames/v0001/?key={self.apiKey}&steamid={steamid64}&format=json'
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.JSONDecodeError as e:
            logger.error(f"Steam API returned invalid JSON: {str(e)}")
            return {"response": {'games': []}}
        except requests.exceptions.RequestException as e:
            logger.error(f"Steam API request failed: {str(e)}")
            return {"response": {'games': []}}

