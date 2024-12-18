from django.db import models
'''
Deadlock API hero names by ID Number:
Infernus: 1
Seven: 2
Vindicta: 3
Lady Geist: 4
Abrams: 5
'''
class HeroesModel(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    abilities = models.JSONField()
    wins = models.BigIntegerField()
    losses = models.BigIntegerField()