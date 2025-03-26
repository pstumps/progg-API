from rest_framework import serializers

from ..Models.PlayerRecords import PlayerRecords, record_indexes


class PlayerRecordsSerializer(serializers.ModelSerializer):

    class Meta:
        model = PlayerRecords


    def to_representation(self, obj):
        records = {}
        k = obj.records[record_indexes['kills']]
        records['kills'] = {'hero': k[0], 'value': k[1], 'matchId': k[2]}
        a = obj.records[record_indexes['assists']]
        records['assists'] = {'hero': a[0], 'value': a[1], 'matchId': a[2]}
        hd = obj.records[record_indexes['heroDamage']]
        records['heroDmg'] = {'hero': hd[0], 'value': hd[1], 'matchId': hd[2]}
        od = obj.records[record_indexes['objDamage']]
        records['objDmg'] = {'hero': od[0], 'value': od[1], 'matchId': od[2]}
        h = obj.records[record_indexes['healing']]
        records['healing'] = {'hero': h[0], 'value': h[1], 'matchId': h[2]}
        s = obj.records[record_indexes['souls']]
        records['souls'] = {'hero': s[0], 'value': s[1], 'matchId': s[2]}
        # lh = obj.records[record_indexes['lastHits']]
        # records['lastHits'] = {'heroId': lh[0], 'value': lh[1]}
        return records