from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from pr_app.models import Team, User


class TeamApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_team_add_creates_team_and_members(self):
        payload = {
            "team_name": "backend",
            "members": [
                {"user_id": "u1", "username": "Alice", "is_active": True},
                {"user_id": "u2", "username": "Bob", "is_active": False},
            ],
        }
        resp = self.client.post("/team/add", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.json()
        self.assertEqual(data["team_name"], "backend")
        self.assertEqual(len(data["members"]), 2)
        team = Team.objects.get(name="backend")
        self.assertEqual(team.members.count(), 2)
        u1 = User.objects.get(user_id="u1")
        u2 = User.objects.get(user_id="u2")
        self.assertTrue(u1.is_active)
        self.assertFalse(u2.is_active)
        self.assertEqual(u1.team, team)
        self.assertEqual(u2.team, team)

    def test_team_add_duplicate_team_returns_team_exists(self):
        Team.objects.create(name="backend")
        payload = {
            "team_name": "backend",
            "members": [],
        }
        resp = self.client.post("/team/add", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        data = resp.json()
        self.assertIn("error", data)
        self.assertEqual(data["error"]["code"], "TEAM_EXISTS")

    def test_team_get_existing_team(self):
        team = Team.objects.create(name="backend")
        User.objects.create(
            user_id="u1",
            username="Alice",
            team=team,
            is_active=True,
        )
        resp = self.client.get("/team/get", {"team_name": "backend"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(data["team_name"], "backend")
        self.assertEqual(len(data["members"]), 1)
        self.assertEqual(data["members"][0]["user_id"], "u1")

    def test_team_get_not_found(self):
        resp = self.client.get("/team/get", {"team_name": "unknown"})
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = resp.json()
        self.assertEqual(data["error"]["code"], "NOT_FOUND")

    def test_team_get_without_team_name_returns_bad_request(self):
        resp = self.client.get("/team/get")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        data = resp.json()
        self.assertIn("error", data)
        self.assertEqual(data["error"]["code"], "BAD_REQUEST")
