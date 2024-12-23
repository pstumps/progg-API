from proggbackend.services import deadlockAPIAnalyticsService, deadlockAPIDataService
from .Models.HeroesModel import HeroesModel

import numpy as np

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

class proGGAPIHeroesService:

    def updateHeroes(self):
        # TODO: Configure to run every 6 hours at some point
        # Updates heroes stats models in database

        DLAPIAnalyticsService = deadlockAPIAnalyticsService()
        DLAPIDataService = deadlockAPIDataService()

        latest_patch_timestamp = DLAPIDataService.getLatestPatchUnixTimestamp()
        data = DLAPIAnalyticsService.getHeroesWinLossStats(min_unix_timestamp=latest_patch_timestamp)

        if data:
            total_matches = sum(stats['matches'] for stats in data)
            for stats in data:
                heroName = HeroesDict.get(stats['hero_id'])
                if not heroName:
                    continue

                try:
                    hero = HeroesModel.objects.get(name=heroName)
                except HeroesModel.DoesNotExist:
                    hero = HeroesModel.objects.create(name=heroName)

                hero.wins = stats['wins']
                hero.losses = stats['losses']
                hero.kills = stats['total_kills']
                hero.deaths = stats['total_deaths']
                hero.assists = stats['total_assists']
                hero.matches = stats['matches']

                # active_matches = DLAPIDataService.getActiveMatches()
                # if active_matches:
                #    highest_match = active_matches[-1]['match_id']
                #    hero.pickrate = round((stats['matches'] / highest_match) * 100, 2)
                if total_matches > 0:
                    hero.pickrate = round((stats['matches'] / total_matches) * 100, 2)

                hero.save()
        else:
            raise Exception('No data returned from Deadlock API')

    def getAllHeroes(self):
        heroes = HeroesModel.objects.all()
        data = []
        for hero in heroes:
            data.append({
                'name': hero.name,
                'tier': hero.tier,
                'winrate': self.calculateWinRate(hero.wins, hero.losses),
                'kda': self.calculateKDA(hero.kills, hero.deaths, hero.assists),
                'pickrate': hero.pickrate,
                'beta': hero.beta,
                'abilities': hero.abilities
            })

        return {'heroes': data}

    def getHeroByName(self, hero_name):
        try:
            hero = HeroesModel.objects.get(name=hero_name)
            data = {
                'name': hero.name,
                'tier': hero.tier,
                'winrate': self.calculateWinRate(hero.wins, hero.losses),
                'kda': self.calculateKDA(hero.kills, hero.deaths, hero.assists),
                'pickrate': hero.pickrate,
                'abilities': hero.abilities
            }
            return data
        except HeroesModel.DoesNotExist:
            return None


    def calculateTierForEachHero(self):
        all_heroes = HeroesModel.objects.filter(beta=False)
        scores = []

        max_kda = 0
        max_matches = 0

        for hero in all_heroes:
            kda = self.calculateKDA(hero.kills, hero.deaths, hero.assists)
            if kda > max_kda:
                max_kda = kda
            if hero.matches > max_matches:
                max_matches = hero.matches

        for hero in all_heroes:
            score = self.calculateScore(hero, max_kda, max_matches)
            scores.append(score)

        mean = np.mean(scores)
        std = np.std(scores)

        z_scores = [(s - mean) / std for s in scores]

        sorted_zscores = sorted(z_scores)

        scores.sort()
        s_threshold = sorted_zscores[int(0.9 * len(sorted_zscores))]
        a_threshold = sorted_zscores[int(0.7 * len(sorted_zscores))]
        b_threshold = sorted_zscores[int(0.5 * len(sorted_zscores))]
        c_threshold = sorted_zscores[int(0.3 * len(sorted_zscores))]

        for hero in all_heroes:
            score = self.calculateScore(hero, max_kda, max_matches)
            z_score = (score - mean) / std

            if z_score >= s_threshold:
                hero.tier = 'S'
            elif z_score >= a_threshold:
                hero.tier = 'A'
            elif z_score >= b_threshold:
                hero.tier = 'B'
            elif z_score >= c_threshold:
                hero.tier = 'C'
            else:
                hero.tier = 'D'
            hero.save()

    def calculateScore(self, hero, max_kda, max_matches):
        winrate = self.calculateWinRate(hero.wins, hero.losses)
        kda = self.calculateKDA(hero.kills, hero.deaths, hero.assists)
        #pickrate = hero.pickrate
        matches = hero.matches

        winrate_weight = 0.5
        kda_weight = 0.2
        #pickrate_weight = 0.05
        matches_weight = 0.1

        normalized_winrate = winrate / 100
        normalized_kda = min(kda / max_kda, 1)
        #normalized_pickrate = min(pickrate / 100, 1)
        normalized_matches = min(matches / max_matches, 1)

        score = ((normalized_winrate * winrate_weight) +
                 (normalized_kda * kda_weight) +
                 #(normalized_pickrate * pickrate_weight) +
                 (normalized_matches * matches_weight))

        '''
        if score > 0.8:
            return 'S'
        elif score > 0.6:
            return 'A'
        elif score > 0.5:
            return 'B'
        elif score > 0.4:
            return 'C'
        else:
            return 'D'
        '''

        return score


    def calculateWinRate(self, wins, losses):
        return round((wins / (wins + losses) * 100), 1)

    def calculateKDA(self, kills, deaths, assists):
        return round(((kills + assists) / deaths), 2)
