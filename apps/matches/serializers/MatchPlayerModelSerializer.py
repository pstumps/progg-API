from rest_framework import serializers
from apps.matches.Models import MatchPlayerModel


class MatchPlayerModelSerailizer(serializers.ModelSerializer):


    class Meta:
        model = MatchPlayerModel
        fields = '__all__'


