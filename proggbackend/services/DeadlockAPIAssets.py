import requests
from django.conf import settings

import json

BASE_DIR = settings.BASE_DIR

class deadlockAPIAssetsService:
    def __init__(self):
        self.base_url = 'https://assets.deadlock-api.com'

    def getHeroAssets(self):
        print('Getting hero assets from assets.deadlock-api...')
        url = self.base_url + '/v2/heroes'
        response = requests.get(url)
        return response.json()

    def getHeroAssetsById(self, hero_id):
        print('Getting hero assets by id from assets.deadlock-api...')
        url = self.base_url + '/v2/heroes/' + str(hero_id)
        response = requests.get(url)
        return response.json()

    def getItemAssets(self):
        print('Getting item assets from assets.deadlock-api...')
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
        with open(str(BASE_DIR) + '\\proggbackend\\ItemData_IDIndexed.json') as f:
            response = json.load(f)
        return response


    def getItemsDictIndexedByClassname(self):
        with open(str(BASE_DIR) + '\\proggbackend\\ItemData_ClassNameIndexed.json') as f:
            response = json.load(f)
        return response