from djoser.serializers import UserSerializer
from .models import User
from rest_framework import serializers
from django.contrib.auth.models import Group


class UserSerializer(UserSerializer):
    groups = serializers.StringRelatedField(many=True)

    class Meta:
        model = User
        fields = (
            "email",
            "groups",
        )
