import requests

from .Models.HeroesModel import HeroesModel


class deadlockAnalyticsAPIService:
    base_url = 'https://analytics.deadlock-api.com'

    HeroesDict = {
        1: 'Infernus',
        2: 'Seven',
        3: 'Vindicta',
        4: 'Lady Geist',
        5: 'Abrams',
        7: 'Wraith',
        8: 'McGinnis',
        10: 'Paradox',
        11: 'Dynamo',
        12: 'Kelvin',
        13: 'Haze',
        14: 'Holliday',
        15: 'Bebop',
        16: 'Calico',
        17: 'Grey Talon',
        18: 'Mo & Krill',
        19: 'Shiv',
        20: 'Ivy',
        25: 'Warden',
        27: 'Yamato',
        31: 'Lash',
        35: 'Viscous',
        48: 'Wrecker',
        50: 'Pocket',
        52: 'Mirage',
        53: 'Fathom',
        58: 'Viper',
        60: 'Magician',
        61: 'Trapper',
        62: 'Raven',
    }

    def getHeroesStats(self):
        # TODO: Configure to run every 6 hours at some point
        url = self.base_url + '/v2/hero-win-loss-stats'
        response = requests.get(url)
        return response.json()

    def updateHeroes(self, data):
        # Updates heroes stats models in database
        for stats in data:
            heroName = self.HeroesDict.get(stats['hero_id'])
            if not heroName:
                continue

            try:
                hero = HeroesModel.objects.get(name=heroName)
            except HeroesModel.DoesNotExist:
                hero = HeroesModel.objects.create(name=heroName)

            hero.wins = stats['wins']
            hero.losses = stats['losses']
            hero.kills = stats['kills']
            hero.deaths = stats['deaths']
            hero.assists = stats['assists']
            hero.save()
