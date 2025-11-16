from rest_framework import serializers

from ..models import User
from .pull_requests import PullRequestShortSerializer


class UserSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source="team.name")

    class Meta:
        model = User
        fields = ("user_id", "username", "team_name", "is_active")


class SetIsActiveSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    is_active = serializers.BooleanField()


class UserReviewResponseSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    pull_requests = PullRequestShortSerializer(many=True)
