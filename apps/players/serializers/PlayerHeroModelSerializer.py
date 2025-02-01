from rest_framework import serializers

from ..Models.PlayerHeroModel import PlayerHeroModel

class PlayerHeroModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerHeroModel
        fields = '__all__'