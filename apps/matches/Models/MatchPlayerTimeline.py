from django.db import models
from MatchesModel import MatchesModel
from MatchPlayerModel import MatchPlayerModel

class MatchPlayerTimelineEvent(models.Model):
    timeline_event_id = models.AutoField(primary_key=True)
    match = models.ForeignKey(MatchesModel, related_name='matchPlayerTimelineEvents', on_delete=models.CASCADE)
    match_player = models.ForeignKey(MatchPlayerModel, related_name='matchPlayerTimelineEvents', on_delete=models.CASCADE)
    date = models.DateTimeField(null=True)
    timestamp = models.IntegerField(default=0)
    event_type = models.CharField(max_length=100, null=True) # Kill, death, item, or level
    event_data = models.JSONField(null=True)


