from django.db import models
from .MatchesModel import MatchesModel
from .MatchPlayerModel import MatchPlayerModel


class MatchPlayerTimelineEvent(models.Model):
    timeline_event_id = models.AutoField(primary_key=True)
    match = models.ForeignKey(MatchesModel, related_name='matchPlayerTimelineEvents', on_delete=models.CASCADE)
    matchPlayer = models.ForeignKey(MatchPlayerModel, related_name='matchPlayerTimelineEvents', on_delete=models.CASCADE)
    timestamp = models.IntegerField(default=0)
    type = models.CharField(max_length=10, null=True)
    details = models.JSONField(null=True)


