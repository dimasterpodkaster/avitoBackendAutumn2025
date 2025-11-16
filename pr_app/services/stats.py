from __future__ import annotations
from django.db.models import Count

from ..models import User


def get_reviewer_stats():
    return (User.objects.annotate(review_count=Count("assigned_pull_requests")).filter(review_count__gt=0)
            .select_related("team").order_by("-review_count", "user_id"))
