from . import models
from rest_framework import serializers

# Create your serializers here.


class PredictionInputSerializer(serializers.Serializer):
    nom_patient = serializers.CharField(max_length=100, required=False)
    DAO = serializers.FloatField()


class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Prediction
        fields = "__all__"
