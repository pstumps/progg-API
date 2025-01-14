from proggbackend.services import deadlockAPIAnalyticsService, deadlockAPIDataService


class proggAPIMatchesService:
    def __init__(self):
        self.DLAPIAnalyticsService = deadlockAPIAnalyticsService()
        self.DLAPIDataService = deadlockAPIDataService()
