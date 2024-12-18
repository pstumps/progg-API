from django.db import models
'''
Deadlock API hero names by ID Number:
Infernus: 1
Seven: 2
Vindicta: 3
Lady Geist: 4
Abrams: 5
Wraith: 7
McGinnis: 8
Paradox: 10
Dynamo: 11
Kelvin: 12
Haze: 13
Holliday (beta): 14 
Bebop: 15
Calico (beta): 16
Grey Talon: 17
Mo & Krill: 18
Shiv: 19
Ivy: 20
Warden: 25
Yamato: 27
Lash: 31
Viscous: 35
Wrecker (beta): 48
Pocket: 50
Mirage: 52
Fathom (beta): 53
Viper (beta): 58
Magician (beta): 60
Trapper (beta): 61
Raven (beta): 62
'''


class HeroesModel(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False)
    description = models.TextField()
    abilities = models.JSONField()
    wins = models.BigIntegerField()
    losses = models.BigIntegerField()
    kills = models.BigIntegerField()
    deaths = models.BigIntegerField()
    assists = models.BigIntegerField()