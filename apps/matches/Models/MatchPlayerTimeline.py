from django.db import models
from MatchesModel import MatchesModel
from ...players.Models.PlayerModel import PlayerModel

class MatchPlayerTimelineEvent(models.Model):
    timeline_event_id = models.AutoField(primary_key=True)
    match = models.ForeignKey(MatchesModel, related_name='matchPlayerTimelineEvents', on_delete=models.CASCADE)
    player = models.ForeignKey(PlayerModel, related_name='matchPlayerTimelineEvents', on_delete=models.CASCADE)
    timestamp = models.IntegerField(default=0)
    eventType = models.CharField(max_length=100, null=True) # Kill, death, item, or level
    eventData = models.JSONField(null=True)


