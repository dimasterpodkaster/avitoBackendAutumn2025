from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from ..models import PullRequest, User
from ..exceptions import (PullRequestExistsError, NotFoundError, PullRequestMergedError, ReviewerNotAssignedError,
                          NoCandidateError)


@transaction.atomic
def create_pull_request(pull_request_id: str, pull_request_name: str, author_id: str) -> PullRequest:
    if PullRequest.objects.filter(pk=pull_request_id).exists():
        raise PullRequestExistsError()
    try:
        author = User.objects.select_related("team").get(pk=author_id)
    except User.DoesNotExist:
        raise NotFoundError()
    pr = PullRequest.objects.create(pull_request_id=pull_request_id, name=pull_request_name, author=author)

    _assign_initial_reviewers(pr, author)
    return pr


def _assign_initial_reviewers(pr: PullRequest, author: User) -> None:
    team = author.team
    candidates = (User.objects.filter(team=team, is_active=True).exclude(pk=author.pk))
    selected = list(candidates.order_by("?")[:2])
    if not selected:
        return
    pr.reviewers.add(*selected)


@transaction.atomic
def merge_pull_request(pull_request_id: str) -> PullRequest:
    try:
        pr = PullRequest.objects.get(pk=pull_request_id)
    except PullRequest.DoesNotExist:
        raise NotFoundError("pull request not found")
    if pr.is_merged:
        return pr
    pr.status = PullRequest.STATUS_MERGED
    pr.merged_at = timezone.now()
    pr.save(update_fields=["status", "merged_at"])
    return pr


@transaction.atomic
def reassign_reviewer(pull_request_id: str, old_user_id: str) -> tuple[PullRequest, User, User]:
    try:
        pr = PullRequest.objects.select_related("author").get(pk=pull_request_id)
    except PullRequest.DoesNotExist:
        raise NotFoundError()
    if pr.is_merged:
        raise PullRequestMergedError("cannot reassign on merged PR")
    try:
        old_reviewer = User.objects.select_related("team").get(pk=old_user_id)
    except User.DoesNotExist:
        raise NotFoundError()
    if not pr.reviewers.filter(pk=old_reviewer.pk).exists():
        raise ReviewerNotAssignedError()
    team = old_reviewer.team
    candidates = (User.objects.filter(team=team, is_active=True).exclude(pk=old_reviewer.pk).exclude(pk=pr.author.pk))
    new_reviewer = candidates.order_by("?").first()
    if new_reviewer is None:
        raise NoCandidateError()
    pr.reviewers.remove(old_reviewer)
    pr.reviewers.add(new_reviewer)
    return pr, old_reviewer, new_reviewer
