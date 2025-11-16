from rest_framework import serializers

from ..models import PullRequest, User


class PullRequestSerializer(serializers.ModelSerializer):
    pull_request_name = serializers.CharField(source="name")
    author_id = serializers.CharField(source="author.user_id")
    assigned_reviewers = serializers.SlugRelatedField(source="reviewers", many=True, read_only=True,
                                                      slug_field="user_id")
    createdAt = serializers.DateTimeField(source="created_at")
    mergedAt = serializers.DateTimeField(source="merged_at", allow_null=True)

    class Meta:
        model = PullRequest
        fields = ("pull_request_id", "pull_request_name", "author_id", "status", "assigned_reviewers", "createdAt",
                  "mergedAt",)


class PullRequestShortSerializer(serializers.ModelSerializer):
    pull_request_name = serializers.CharField(source="name")
    author_id = serializers.CharField(source="author.user_id")

    class Meta:
        model = PullRequest
        fields = ("pull_request_id", "pull_request_name", "author_id", "status",)


class PullRequestCreateSerializer(serializers.Serializer):
    pull_request_id = serializers.CharField()
    pull_request_name = serializers.CharField()
    author_id = serializers.CharField()


class PullRequestMergeSerializer(serializers.Serializer):
    pull_request_id = serializers.CharField()


class PullRequestReassignSerializer(serializers.Serializer):
    pull_request_id = serializers.CharField()
    old_user_id = serializers.CharField()
