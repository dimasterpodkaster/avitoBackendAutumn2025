from rest_framework import serializers

from ..models import User


class ReviewerStatsSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source="team.name")
    review_count = serializers.IntegerField()

    class Meta:
        model = User
        fields = ("user_id", "username", "team_name", "review_count")
