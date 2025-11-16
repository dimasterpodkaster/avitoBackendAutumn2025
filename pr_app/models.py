from django.db import models
from django.utils import timezone


class Team(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "teams"
        verbose_name = "Team"
        verbose_name_plural = "Teams"


class User(models.Model):
    user_id = models.CharField(max_length=64, primary_key=True)
    username = models.CharField(max_length=255)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="members")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"


class PullRequest(models.Model):
    STATUS_OPEN = "OPEN"
    STATUS_MERGED = "MERGED"

    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_MERGED, "Merged"),
    ]

    pull_request_id = models.CharField(max_length=64, primary_key=True)
    name = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="authored_pull_requests")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_OPEN)
    reviewers = models.ManyToManyField(User, related_name="assigned_pull_requests", blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    merged_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "pull_requests"
        verbose_name = "Pull Request"
        verbose_name_plural = "Pull Requests"
        ordering = ["-created_at"]

    @property
    def is_merged(self) -> bool:
        return self.status == self.STATUS_MERGED
