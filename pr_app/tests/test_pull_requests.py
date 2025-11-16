from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from pr_app.models import Team, User, PullRequest


class PullRequestApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.team = Team.objects.create(name="backend")
        self.author = User.objects.create(
            user_id="author",
            username="Author",
            team=self.team,
            is_active=True,
        )
        self.reviewer1 = User.objects.create(
            user_id="u1",
            username="Reviewer 1",
            team=self.team,
            is_active=True,
        )
        self.reviewer2 = User.objects.create(
            user_id="u2",
            username="Reviewer 2",
            team=self.team,
            is_active=True,
        )
        self.inactive = User.objects.create(
            user_id="u3",
            username="Inactive",
            team=self.team,
            is_active=False,
        )

    def test_create_pr_assigns_up_to_two_active_reviewers(self):
        payload = {
            "pull_request_id": "pr1",
            "pull_request_name": "Initial PR",
            "author_id": "author",
        }
        resp = self.client.post("/pullRequest/create", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.json()
        self.assertEqual(data["pull_request_id"], "pr1")
        self.assertEqual(data["author_id"], "author")
        assigned = data["assigned_reviewers"]
        self.assertLessEqual(len(assigned), 2)
        self.assertNotIn("author", assigned)
        self.assertNotIn("u3", assigned)

    def test_create_pr_when_no_other_members_assigns_zero_reviewers(self):
        empty_team = Team.objects.create(name="solo")
        solo_author = User.objects.create(
            user_id="u4",
            username="Solo",
            team=empty_team,
            is_active=True,
        )
        payload = {
            "pull_request_id": "pr2",
            "pull_request_name": "Solo PR",
            "author_id": "u4",
        }
        resp = self.client.post("/pullRequest/create", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.json()
        self.assertEqual(data["pull_request_id"], "pr2")
        self.assertEqual(len(data["assigned_reviewers"]), 0)

    def test_create_pr_unknown_author_returns_not_found(self):
        payload = {
            "pull_request_id": "pr3",
            "pull_request_name": "Unknown author",
            "author_id": "unknown",
        }
        resp = self.client.post("/pullRequest/create", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = resp.json()
        self.assertEqual(data["error"]["code"], "NOT_FOUND")

    def test_create_pr_duplicate_id_returns_conflict(self):
        PullRequest.objects.create(
            pull_request_id="pr1",
            name="Existing",
            author=self.author,
        )
        payload = {
            "pull_request_id": "pr1",
            "pull_request_name": "Duplicate",
            "author_id": "author",
        }
        resp = self.client.post("/pullRequest/create", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
        data = resp.json()
        self.assertEqual(data["error"]["code"], "PR_EXISTS")

    def test_merge_pr_changes_status_and_sets_merged_at(self):
        pr = PullRequest.objects.create(
            pull_request_id="pr1",
            name="To merge",
            author=self.author,
        )
        payload = {"pull_request_id": "pr1"}
        resp = self.client.post("/pullRequest/merge", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(data["status"], "MERGED")
        self.assertIsNotNone(data["mergedAt"])

    def test_merge_pr_is_idempotent(self):
        pr = PullRequest.objects.create(
            pull_request_id="pr1",
            name="To merge",
            author=self.author,
        )
        payload = {"pull_request_id": "pr1"}
        resp1 = self.client.post("/pullRequest/merge", payload, format="json")
        self.assertEqual(resp1.status_code, status.HTTP_200_OK)
        data1 = resp1.json()
        resp2 = self.client.post("/pullRequest/merge", payload, format="json")
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        data2 = resp2.json()
        self.assertEqual(data1["status"], "MERGED")
        self.assertEqual(data2["status"], "MERGED")
        self.assertEqual(data1["mergedAt"], data2["mergedAt"])

    def test_merge_pr_not_found(self):
        payload = {"pull_request_id": "unknown"}
        resp = self.client.post("/pullRequest/merge", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = resp.json()
        self.assertEqual(data["error"]["code"], "NOT_FOUND")

    def test_reassign_reviewer_success(self):
        pr = PullRequest.objects.create(
            pull_request_id="pr1",
            name="To reassign",
            author=self.author,
        )
        pr.reviewers.add(self.reviewer1, self.reviewer2)
        payload = {
            "pull_request_id": "pr1",
            "old_user_id": "u1",
        }
        resp = self.client.post("/pullRequest/reassign", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        assigned = data["assigned_reviewers"]
        self.assertNotIn("u1", assigned)
        self.assertIn("u2", assigned)

    def test_reassign_reviewer_not_assigned_returns_conflict(self):
        pr = PullRequest.objects.create(
            pull_request_id="pr1",
            name="PR",
            author=self.author,
        )
        pr.reviewers.add(self.reviewer2)
        payload = {
            "pull_request_id": "pr1",
            "old_user_id": "u1",
        }
        resp = self.client.post("/pullRequest/reassign", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
        data = resp.json()
        self.assertEqual(data["error"]["code"], "NOT_ASSIGNED")

    def test_reassign_reviewer_on_merged_returns_conflict(self):
        pr = PullRequest.objects.create(
            pull_request_id="pr1",
            name="Merged",
            author=self.author,
            status=PullRequest.STATUS_MERGED,
        )
        pr.reviewers.add(self.reviewer1)
        payload = {
            "pull_request_id": "pr1",
            "old_user_id": "u1",
        }
        resp = self.client.post("/pullRequest/reassign", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
        data = resp.json()
        self.assertEqual(data["error"]["code"], "PR_MERGED")

    def test_reassign_reviewer_no_candidate_returns_conflict(self):
        small_team = Team.objects.create(name="small")
        author = User.objects.create(
            user_id="u5",
            username="User 5",
            team=small_team,
            is_active=True,
        )
        only_reviewer = User.objects.create(
            user_id="u6",
            username="Reviewer 6",
            team=small_team,
            is_active=True,
        )
        pr = PullRequest.objects.create(
            pull_request_id="pr2",
            name="No candidate",
            author=author,
        )
        pr.reviewers.add(only_reviewer)
        payload = {
            "pull_request_id": "pr2",
            "old_user_id": "u6",
        }
        resp = self.client.post("/pullRequest/reassign", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
        data = resp.json()
        self.assertEqual(data["error"]["code"], "NO_CANDIDATE")

    def test_reassign_reviewer_pr_not_found(self):
        payload = {
            "pull_request_id": "unknown",
            "old_user_id": "u1",
        }
        resp = self.client.post("/pullRequest/reassign", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = resp.json()
        self.assertEqual(data["error"]["code"], "NOT_FOUND")
