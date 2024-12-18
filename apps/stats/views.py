from django.shortcuts import render
from rest_framework.views import APIView
from .services import deadlockAnalyticsAPIService

# Create your views here.

def updateHeroesStats(request):
    analyticsService = deadlockAnalyticsAPIService()
    data = analyticsService.getHeroesStats()
    try:
        analyticsService.updateHeroes(data)
    except Exception as e:
        print(f'Could not update heroes data, {e}')

    print('Heroes data successfully updated')
