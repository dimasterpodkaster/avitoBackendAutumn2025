from __future__ import annotations
from typing import Iterable, List, Dict, Any
from django.db import transaction

from ..models import User, PullRequest, Team
from ..exceptions import NotFoundError, UnsafeReassignmentError


def set_user_is_active(user_id: str, is_active: bool) -> User:
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise NotFoundError()
    user.is_active = is_active
    user.save(update_fields=["is_active"])
    return user


def get_user_reviews(user_id: str) -> tuple[User, Iterable[PullRequest]]:
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise NotFoundError("user not found")
    prs = (user.assigned_pull_requests.all().select_related("author").order_by("-created_at"))
    return user, prs


@transaction.atomic
def deactivate_team_users(team_name: str, user_ids: List[str]) -> Dict[str, Any]:
    try:
        team = Team.objects.get(name=team_name)
    except Team.DoesNotExist:
        raise NotFoundError("team not found")
    users = list(User.objects.filter(team=team, user_id__in=user_ids, is_active=True))
    if not users:
        raise NotFoundError()
    deactivated_pks = [u.pk for u in users]
    for user in users:
        prs = (PullRequest.objects.filter(status=PullRequest.STATUS_OPEN, reviewers=user).select_related("author"))
        for pr in prs:
            candidates = (User.objects.filter(team=team, is_active=True).exclude(pk__in=deactivated_pks)
                          .exclude(pk=pr.author.pk))
            if not candidates.exists():
                raise UnsafeReassignmentError(f"cannot safely reassign reviewer {user.user_id}, PR {pr.pull_request_id}"
                                              )
    changes: List[Dict[str, str]] = []
    deactivated_ids: List[str] = []
    for user in users:
        user.is_active = False
        user.save(update_fields=["is_active"])
        deactivated_ids.append(user.user_id)
        prs = (PullRequest.objects.filter(status=PullRequest.STATUS_OPEN, reviewers=user).select_related("author"))
        for pr in prs:
            candidates = (User.objects.filter(team=team, is_active=True).exclude(pk__in=deactivated_pks)
                          .exclude(pk=pr.author.pk))
            new_reviewer = candidates.order_by("?").first()
            assert new_reviewer is not None
            pr.reviewers.remove(user)
            pr.reviewers.add(new_reviewer)
            changes.append({"pull_request_id": pr.pull_request_id, "old_reviewer_id": user.user_id,
                            "new_reviewer_id": new_reviewer.user_id})
    return {"team": team, "deactivated_user_ids": deactivated_ids, "changes": changes}
