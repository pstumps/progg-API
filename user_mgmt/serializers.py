from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()
    steam_id3 = serializers.SerializerMethodField()
    player_favorites = serializers.SerializerMethodField()
    match_favorites = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'firstName', 'lastName', 'email', 'phone_number', 'player_favorites', 'match_favorites', 'icon', 'steam_id3' ]

    def get_icon(self, obj):
        return obj.playermodel.icon

    def get_steam_id3(self, obj):
        return obj.playermodel.steam_id3

    def get_player_favorites(self, obj):
        return list(obj.favorites.values_list('steam_id3', flat=True))

    def get_match_favorites(self, obj):
        return list(obj.match_favorites.values_list('deadlock_id', flat=True))

class LoginSerializer(serializers.Serializer):
    password = serializers.CharField()
    username = serializers.EmailField()