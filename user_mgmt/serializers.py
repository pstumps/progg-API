from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    player_favorites = serializers.SerializerMethodField()
    match_favorites = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'firstName', 'lastName', 'email', 'phone_number', 'player_favorites', 'match_favorites']

    def get_player_favorites(self, obj):
        return list(obj.favorites.values_list('steam_id3', flat=True))

    def get_match_favorites(self, obj):
        return list(obj.match_favorites.values_list('steam_id3', flat=True))