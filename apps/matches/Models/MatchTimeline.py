from django.db import models
from MatchesModel import MatchesModel

class MatchTimelineEvent(models.Model):
    timeline_event_id = models.AutoField(primary_key=True)
    match = models.ForeignKey(MatchesModel, related_name='matchTimelineEvents', on_delete=models.CASCADE)
    timestamp = models.IntegerField(default=0)
    eventType = models.CharField(max_length=100, null=True)
    eventData = models.JSONField(null=True)