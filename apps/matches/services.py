import datetime, json
from .Models.MatchesModel import MatchesModel
from proggbackend.services import deadlockAPIAnalyticsService, deadlockAPIDataService



class proggAPIMatchesService:
    def __init__(self):
        self.DLAPIAnalyticsService = deadlockAPIAnalyticsService()
        self.DLAPIDataService = deadlockAPIDataService()

    def createNewMatchFromMetadata(self, dl_match_id):
        matchMetadata = self.DLAPIDataService.getMatchMetadata(dl_match_id=dl_match_id)
        averageBadges = {}
        badgesSum = 0

        for stat, value in matchMetadata['match_info']:
            if stat.startswith('average_badge'):
                averageBadges[stat] = value
                badgesSum += value

        averageBadges['match_average_badge'] = badgesSum / len(averageBadges)

        match = MatchesModel.objects.create(
            deadlock_id=dl_match_id,
            date=datetime.datetime.fromtimestamp(matchMetadata['date'], datetime.timezone.utc),
            averageRank= json.dumps({'badges': averageBadges}),
            gameMode=matchMetadata['game_mode'],
            matchMode=matchMetadata['match_mode'],
            length=matchMetadata['duration_s'],
            victor=matchMetadata['winning_team']
        )


