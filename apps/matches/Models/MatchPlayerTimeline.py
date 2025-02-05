from django.db import models
from .MatchesModel import MatchesModel
from apps.players.Models.PlayerModel import PlayerModel


class MatchPlayerTimelineEvent(models.Model):
    timeline_event_id = models.AutoField(primary_key=True)
    match = models.ForeignKey(MatchesModel, related_name='matchPlayerTimelineEvents', on_delete=models.CASCADE)
    player = models.ForeignKey(PlayerModel, related_name='matchPlayerTimelineEvents', on_delete=models.CASCADE, null=True)
    timestamp = models.IntegerField(default=0)
    type = models.CharField(max_length=10, null=True)
    details = models.JSONField(null=True)


