from rest_framework import serializers

from ..models import Team, User


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("user_id", "username", "is_active")


class TeamSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source="name")
    members = TeamMemberSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = ("team_name", "members")
