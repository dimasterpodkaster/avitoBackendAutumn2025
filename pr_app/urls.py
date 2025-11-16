from django.urls import path
from .views import (TeamAddView, TeamGetView, TeamDeactivateUsersView, SetIsActiveView, GetReviewView,
                    PullRequestCreateView, PullRequestMergeView, PullRequestReassignView, HealthView, ReviewerStatsView)

urlpatterns = [
    path("team/add", TeamAddView.as_view()),
    path("team/get", TeamGetView.as_view()),
    path("team/deactivateUsers", TeamDeactivateUsersView.as_view()),
    path("users/setIsActive", SetIsActiveView.as_view()),
    path("users/getReview", GetReviewView.as_view()),
    path("pullRequest/create", PullRequestCreateView.as_view()),
    path("pullRequest/merge", PullRequestMergeView.as_view()),
    path("pullRequest/reassign", PullRequestReassignView.as_view()),
    path("health", HealthView.as_view()),
    path("stats/reviewers", ReviewerStatsView.as_view()),
]
