from django.db import models

# Each record is saved as an array with the following structure for each index:
#  [heroID, value]
# Index structure is as follows:
# [0] = kills, [1] = assists, [2] = heroDamage, [3] = objDamage, [4] = healing,  [5] = souls, [6] = lastHits

def default_records():
    return [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]

record_indexes = {
    'kills': 0,
    'assists': 1,
    'heroDamage': 2,
    'objDamage': 3,
    'healing': 4,
    'souls': 5,
    'lastHits': 6
}

class PlayerRecords(models.Model):

    player = models.ForeignKey('players.PlayerModel', on_delete=models.CASCADE)
    records = models.JSONField(default=default_records, null=True)

    def updateRecord(self, recordType, heroId, newValue):
        record_idx = record_indexes.get(recordType)
        currentRecord = self.records[record_idx]
        if newValue > currentRecord[1]:
            self.records[record_idx] = [heroId, newValue]
            self.save()
