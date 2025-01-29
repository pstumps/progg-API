from rest_framework import serializers
from apps.matches.Models.MatchesModel import MatchesModel


class MatchModelSerailizer(serializers.ModelSerializer):
    class Meta:
        model = MatchesModel
        fields = '__all__'




