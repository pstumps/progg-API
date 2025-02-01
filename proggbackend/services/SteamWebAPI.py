from pathlib import Path
import os, environ, requests

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
API_KEY = env('STEAM_WEB_API_KEY')

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
        steamid64 = self.convertSteamID3ToSteamID64(steam_id3)
        url = f'{self.ISteamUserBaseURL}/GetPlayerSummaries/v0002/?key={self.apiKey}&steamids={steamid64}&format=json'
        response = requests.get(url)
        return response.json()

    def getOwnedGames(self, steam_id3):
        steamid64 = self.convertSteamID3ToSteamID64(steam_id3)
        url = f'{self.IPlayerServiceBaseURL}/GetOwnedGames/v0001/?key={self.apiKey}&steamid={steamid64}&format=json'
        #url = url + '&input_json={appids_filter: [1422450]}'
        response = requests.get(url)
        return response.json()
