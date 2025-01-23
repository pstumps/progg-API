from rest_framework import serializers
from .Models.PlayerModel import PlayerModel
from .Models.PlayerHeroModel import PlayerHeroModel

class PlayerModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerModel
        fields = '__all__'

class PlayerHeroModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerHeroModel
        fields = '__all__'