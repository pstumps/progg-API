from rest_framework.throttling import UserRateThrottle

class StatsRateThrottle(UserRateThrottle):
    scope = 'stats'