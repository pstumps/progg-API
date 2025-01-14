from django.db import models
from ...matches.Models.MatchesModel import MatchesModel
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
    description = models.TextField(null=True)
    abilities = models.JSONField(null=True)
    wins = models.BigIntegerField(null=True)
    losses = models.BigIntegerField(null=True)
    kills = models.BigIntegerField(null=True)
    deaths = models.BigIntegerField(null=True)
    assists = models.BigIntegerField(null=True)
    matches = models.BigIntegerField(null=True)
    pickrate = models.IntegerField(null=True)
    tier = models.CharField(max_length=1, null=True)
    beta = models.BooleanField(null=True)
    matchesModel = models.ManyToManyField(MatchesModel, related_name='heroesModel', null=True)