from rest_framework import serializers

from .teams import TeamSerializer


class TeamDeactivateUsersRequestSerializer(serializers.Serializer):
    team_name = serializers.CharField()
    user_ids = serializers.ListField(child=serializers.CharField(), allow_empty=False)


class DeactivationChangeSerializer(serializers.Serializer):
    pull_request_id = serializers.CharField()
    old_reviewer_id = serializers.CharField()
    new_reviewer_id = serializers.CharField(allow_null=True)


class TeamDeactivateUsersResponseSerializer(serializers.Serializer):
    team = TeamSerializer()
    deactivated_user_ids = serializers.ListField(child=serializers.CharField())
    changes = DeactivationChangeSerializer(many=True)
