from __future__ import annotations


class DomainError(Exception):
    code = "UNKNOWN"

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)

    @property
    def default_message(self) -> str:
        return "domain error"


class TeamExistsError(DomainError):
    code = "TEAM_EXISTS"

    @property
    def default_message(self) -> str:
        return "team_name already exists"


class PullRequestExistsError(DomainError):
    code = "PR_EXISTS"

    @property
    def default_message(self) -> str:
        return "PR id already exists"


class PullRequestMergedError(DomainError):
    code = "PR_MERGED"

    @property
    def default_message(self) -> str:
        return "cannot reassign on merged PR"


class ReviewerNotAssignedError(DomainError):
    code = "NOT_ASSIGNED"

    @property
    def default_message(self) -> str:
        return "reviewer is not assigned to this PR"


class NoCandidateError(DomainError):
    code = "NO_CANDIDATE"

    @property
    def default_message(self) -> str:
        return "no active replacement candidate in team"


class NotFoundError(DomainError):
    code = "NOT_FOUND"

    @property
    def default_message(self) -> str:
        return "resource not found"


class BadRequestError(DomainError):
    code = "BAD_REQUEST"

    @property
    def default_message(self) -> str:
        return "bad request"


class UnsafeReassignmentError(DomainError):
    code = "UNSAFE_REASSIGN"

    @property
    def default_message(self):
        return "cannot safely reassign reviewers for all open PRs"
