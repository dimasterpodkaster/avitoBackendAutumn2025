from __future__ import annotations
from typing import Iterable
from django.db import transaction

from ..models import Team, User
from ..exceptions import TeamExistsError, NotFoundError


@transaction.atomic
def create_team_with_members(team_name: str, members: Iterable[dict]) -> Team:
    if Team.objects.filter(name=team_name).exists():
        raise TeamExistsError()
    team = Team.objects.create(name=team_name)
    for member in members:
        user_id = member["user_id"]
        username = member["username"]
        is_active = bool(member.get("is_active", True))
        User.objects.update_or_create(user_id=user_id, defaults={"username": username, "team": team,
                                                                 "is_active": is_active},)
    return team


def get_team_with_members(team_name: str) -> Team:
    try:
        return Team.objects.prefetch_related("members").get(name=team_name)
    except Team.DoesNotExist:
        raise NotFoundError()
