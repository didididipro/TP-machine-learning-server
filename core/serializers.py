from . import models
from rest_framework import serializers

# Create your serializers here.


class PredictionInputSerializer(serializers.Serializer):
    id_sample = serializers.CharField(
        max_length=100, required=False, default="unknown"
    )
    DAO = serializers.FloatField()


class PredictionOutputSerializer(serializers.Serializer):
    id_sample = serializers.CharField(max_length=100)
    prediction = serializers.CharField(max_length=50)
    confidence = serializers.CharField(max_length=10)
