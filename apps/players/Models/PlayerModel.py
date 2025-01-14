from django.db import models

class PlayerModel(models.Model):
    player_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    player_tag = models.CharField(max_length=100)
    avatar = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    rank = models.IntegerField(null=True)
    level = models.IntegerField(null=True)
    heroes = models.ManyToManyField('heroes.HeroesModel', related_name='players_model', symmetrical=True)
    matches = models.ManyToManyField('matches.MatchesModel', related_name='players_model', symmetrical=True)
    winrate = models.FloatField(null=True)
    kda = models.FloatField(null=True)
    heroDamage = models.BigIntegerField(null=True)
    objDamage = models.BigIntegerField(null=True)
    healing = models.BigIntegerField(null=True)
    souls = models.BigIntegerField(null=True)
    mmr = models.BigIntegerField(null=True)
    lastMatch = models.DateTimeField(null=True)
    lastLogin = models.DateTimeField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name