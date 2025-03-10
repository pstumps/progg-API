from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    favorites = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'firstName', 'lastName', 'email', 'phone_number', 'favorites']

    def get_favorites(self, obj):
        # Return a list of steam_id3 values instead of PlayerModel instances
        return list(obj.favorites.values_list('steam_id3', flat=True))