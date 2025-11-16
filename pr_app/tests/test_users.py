from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from pr_app.models import Team, User, PullRequest


class UserApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.team = Team.objects.create(name="backend")
        self.user = User.objects.create(
            user_id="u1",
            username="Alice",
            team=self.team,
            is_active=True,
        )

    def test_set_is_active_updates_flag(self):
        payload = {"user_id": "u1", "is_active": False}
        resp = self.client.post("/users/setIsActive", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_set_is_active_user_not_found(self):
        payload = {"user_id": "unknown", "is_active": False}
        resp = self.client.post("/users/setIsActive", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = resp.json()
        self.assertEqual(data["error"]["code"], "NOT_FOUND")

    def test_set_is_active_validation_error_missing_fields(self):
        resp = self.client.post("/users/setIsActive", {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_review_returns_pr_where_user_is_reviewer(self):
        author = User.objects.create(
            user_id="author",
            username="Author",
            team=self.team,
            is_active=True,
        )
        pr1 = PullRequest.objects.create(
            pull_request_id="pr1",
            name="PR 1",
            author=author,
        )
        pr2 = PullRequest.objects.create(
            pull_request_id="pr2",
            name="PR 2",
            author=author,
        )
        pr1.reviewers.add(self.user)
        resp = self.client.get("/users/getReview", {"user_id": "u1"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(data["user_id"], "u1")
        self.assertEqual(len(data["pull_requests"]), 1)
        self.assertEqual(data["pull_requests"][0]["pull_request_id"], "pr1")

    def test_get_review_user_not_found(self):
        resp = self.client.get("/users/getReview", {"user_id": "unknown"})
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = resp.json()
        self.assertEqual(data["error"]["code"], "NOT_FOUND")

    def test_get_review_without_user_id_returns_bad_request(self):
        resp = self.client.get("/users/getReview")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        data = resp.json()
        self.assertIn("error", data)
        self.assertEqual(data["error"]["code"], "BAD_REQUEST")
        