from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from pr_app.models import Team, User, PullRequest


class ReviewerStatsApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.team = Team.objects.create(name="backend")

    def _create_base_data(self):
        u1 = User.objects.create(
            user_id="u1",
            username="Alice",
            team=self.team,
            is_active=True,
        )
        u2 = User.objects.create(
            user_id="u2",
            username="Bob",
            team=self.team,
            is_active=True,
        )
        u3 = User.objects.create(
            user_id="u3",
            username="Charlie",
            team=self.team,
            is_active=False,
        )
        pr1 = PullRequest.objects.create(
            pull_request_id="pr1",
            name="PR1",
            author=u1,
        )
        pr1.reviewers.add(u1, u2)
        pr2 = PullRequest.objects.create(
            pull_request_id="pr2",
            name="PR2",
            author=u2,
        )
        pr2.reviewers.add(u1)
        PullRequest.objects.create(
            pull_request_id="pr3",
            name="PR3",
            author=u1,
        )
        return u1, u2, u3

    def test_reviewer_stats_basic_counts(self):
        self._create_base_data()
        resp = self.client.get("/stats/reviewers")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        ids = {row["user_id"] for row in data}
        self.assertEqual(ids, {"u1", "u2"})
        counts = {row["user_id"]: row["review_count"] for row in data}
        self.assertEqual(counts["u1"], 2)
        self.assertEqual(counts["u2"], 1)
        for row in data:
            self.assertEqual(row["team_name"], "backend")

    def test_reviewer_stats_no_assignments_returns_empty_list(self):
        User.objects.create(
            user_id="u1",
            username="Alice",
            team=self.team,
            is_active=True,
        )
        resp = self.client.get("/stats/reviewers")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])

    def test_reviewer_stats_ordering_by_count_desc_then_user_id(self):
        self._create_base_data()
        resp = self.client.get("/stats/reviewers")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual([row["user_id"] for row in data], ["u1", "u2"])

    def test_inactive_reviewer_is_included_in_stats(self):
        inactive = User.objects.create(
            user_id="u4",
            username="Inactive",
            team=self.team,
            is_active=False,
        )
        pr = PullRequest.objects.create(
            pull_request_id="pr4",
            name="PR 4",
            author=inactive,
        )
        pr.reviewers.add(inactive)

        resp = self.client.get("/stats/reviewers")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        ids = {row["user_id"] for row in data}
        self.assertIn("u4", ids)
