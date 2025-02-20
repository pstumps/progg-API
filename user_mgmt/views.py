from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

'''
def steam_callback_view(request):
    # Suppose user was successfully authenticated by social-auth
    user = request.user  # user is now authenticated
    if user.is_authenticated:
        # If we want to log them in at Django level (session-based):
        login(request, user)

        # Or generate a JWT
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Redirect to Next.js with the token
        frontend_url = f"{settings.FRONTEND_URL}/steam-auth?token={access_token}"
        return redirect(frontend_url)

    # Handle errors or unauthenticated state
    return redirect(settings.FRONTEND_URL + "/login?error=steam_auth_failed")
'''


@api_view(['GET'])
def userAuth(request):
    print("Authenticated user:", request.user)
    if request.user.is_authenticated:
        print('user id is ', request.user.id)
        return Response({
            'detail': 'User is authenticated'
        }, status=200)
    else:
        return Response({
            'detail': 'User is not authenticated'
        }, status=401)
