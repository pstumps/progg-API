from rest_framework import serializers
from .models import MatchesModel


class MatchModelSerailizer(serializers.ModelSerializer):
    class Meta:
        model = MatchesModel
        fields = '__all__'
