from django.http import JsonResponse
from .services import proGGAPIHeroesService
import traceback

def updateStats(request):
    heroes_service = proGGAPIHeroesService()

    try:
        heroes_service.updateHeroes()
        print('Heroes data successfully updated')
        return JsonResponse({'stats': 'success'}, status=200)
    except Exception as e:
        print(f'Could not update heroes data, {e}')
        #TODO: Remove traceback for production
        print(traceback.format_exc())
        return JsonResponse({'stats': 'error', 'message': str(e)}, status=500)

def data(request, hero_name=None):
    heroes_service = proGGAPIHeroesService()

    try:
        if hero_name:
            hero = heroes_service.getHeroByName(hero_name)
            if hero:
                return JsonResponse(hero, status=200)
            else:
                return JsonResponse({'stats': 'error', 'message': '404'}, status=404)
        else:
            all_heroes_data = heroes_service.getAllHeroes()
            return JsonResponse(all_heroes_data, status=200)
    except Exception as e:
        print(f'Could not get heroes data, {e}')
        # TODO: Remove traceback for production
        print(traceback.format_exc())
        return JsonResponse({'stats': 'error', 'message': str(e)}, status=500)

def synergies(request, hero_name=None, min_rank=None, max_rank=None):
    heroes_service = proGGAPIHeroesService()

    try:
        data = heroes_service.calculateHeroCombinationStats(hero_name)
        return JsonResponse(data, status=200)
    except Exception as e:
        print(f'Could not get hero combination data, {e}')

def calculateTier(request):
    heroes_service = proGGAPIHeroesService()

    try:
        heroes_service.calculateTierForEachHero()
        print('Heroes tier successfully calculated')
        return JsonResponse({'stats': 'success'}, status=200)
    except Exception as e:
        print(traceback.format_exc())
        print(f'Could not calculate heroes tier, {e}')

