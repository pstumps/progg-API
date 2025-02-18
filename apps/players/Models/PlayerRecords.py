from django.db import models

# Each record is saved as a JSON object with the following structure:
# {[heroID, value]}
class PlayerRecords(models.Model):
    player = models.ForeignKey('players.PlayerModel', on_delete=models.CASCADE)
    records = models.JSONField(default=dict)

    def updateRecord(self, recordType, heroId, newValue):
        currentRecord = self.records.get(recordType, [None, 0])
        if newValue > currentRecord[1]:
            self.records[recordType] = [heroId, newValue]
            self.save()
