from django.db import models
from .MatchesModel import MatchesModel

class MatchTimelineEvent(models.Model):
    timeline_event_id = models.AutoField(primary_key=True)
    match = models.ForeignKey(MatchesModel, related_name='%(class)s', on_delete=models.CASCADE)
    timestamp = models.IntegerField(default=0)
    team = models.CharField(max_length=50, null=True)

    class Meta:
        abstract = True


class PvPEvent(MatchTimelineEvent):
    slayer_hero_id = models.IntegerField()
    victim_hero_id = models.IntegerField()


class ObjectiveEvent(MatchTimelineEvent):
    # team field is the team whose objective was destroyed
    target = models.CharField(max_length=50)


class MidbossEvent(MatchTimelineEvent):
    # team field is the team that claimed midboss
    slayer = models.CharField(max_length=50)
