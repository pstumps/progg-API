from django.db import models


class MatchesModel(models.Model):
    match_id = models.IntegerField(null=True)
    deadlock_id = models.BigIntegerField(primary_key=True, db_index=True, unique=True)
    metadata_available = models.BooleanField(null=True) # Need to go through and look for all matches that have metadata_available=null and see if metadata is actually available or not.
    processed = models.BooleanField(null=True)
    date = models.BigIntegerField(null=True)
    averageRank = models.JSONField(null=True)
    gameMode = models.CharField(max_length=50, null=True)
    matchMode = models.CharField(max_length=50, null=True)
    length = models.IntegerField(default=0, null=True)
    teamStats = models.JSONField(null=True)
    victor = models.CharField(max_length=50, null=True)
    legacyFourLaneMap = models.BooleanField(default=False, null=True)
    botGame = models.BooleanField(default=False, null=True)

    def save(self, *args, **kwargs):
        if not self.match_id:
            max_id_value = MatchesModel.objects.all().aggregate(
                player_id=models.Max('match_id')
            )['player_id'] or 0

            self.match_id = max_id_value + 1

        super().save(*args, **kwargs)

    def calculateTeamStats(self):
        team_aggregate_stats = self.matchPlayerModels.values('team').annotate(
            kills=models.Sum('kills'),
            deaths=models.Sum('deaths'),
            assists=models.Sum('assists'),
            heroDamage=models.Sum('heroDamage'),
            objDamage=models.Sum('objDamage'),
            healing=models.Sum('healing'),
            souls=models.Sum('souls'),
        )

        # Get rid of the 'team' key in the dictionary
        teamStatsDict = {stat['team']: {k: v for k, v in stat.items() if k != 'team'} for stat in team_aggregate_stats}

        self.teamStats = teamStatsDict
        self.save()


    def rankMatchPlayers(self, match, matchPlayersToCreate):
        def ordinal(n):
            if 10 <= n % 100 <= 20:
                suffix = 'th'
            else:
                suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
            return f"{n}{suffix}"

        def getPlayerScore(matchPlayer):
            killsWeight = 2.0
            deathsWeight = -2.0
            assistsWeight = 1.5
            soulsWeight = 2.5
            heroDamageWeight = 1
            objDamageWeight = 1
            healingWeight = 1
            lastHitsWeight = 0.5
            deniesWeight = 0.5
            accuracyWeight = 0.25

            return (matchPlayer.kills * killsWeight +
                    matchPlayer.deaths * deathsWeight +
                    matchPlayer.assists * assistsWeight +
                    matchPlayer.souls * soulsWeight +
                    matchPlayer.heroDamage * heroDamageWeight +
                    matchPlayer.objDamage * objDamageWeight +
                    matchPlayer.healing * healingWeight +
                    matchPlayer.lastHits * lastHitsWeight +
                    matchPlayer.denies * deniesWeight +
                    matchPlayer.accuracy * accuracyWeight)

        for mp in matchPlayersToCreate:
            mp.score = getPlayerScore(mp)

        matchPlayersToCreate.sort(key=lambda x: x.score, reverse=True)

        losingTeamPlayers = [mp for mp in matchPlayersToCreate if mp.team != match.victor ]

        if losingTeamPlayers:
            svp = max(losingTeamPlayers, key=lambda x: x.score)
        else:
            svp = None

        for rank, mp in enumerate(matchPlayersToCreate, start=1):
            mp.medals = mp.medals or []

            if rank == 1:
                mp.medals.insert(0, 'MVP')
            elif svp is not None and mp.steam_id3 == svp.steam_id3:
                mp.medals.insert(0, 'SVP')
            else:
                mp.medals.insert(0, ordinal(rank))

            mp.save()
