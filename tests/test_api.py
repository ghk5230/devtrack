import json
import unittest

from django.test import Client, SimpleTestCase

from issues.views import ISSUES_FILE, REPORTERS_FILE


class ApiTests(SimpleTestCase):
    def setUp(self):
        self.client = Client()
        self.original_contents = {
            REPORTERS_FILE: REPORTERS_FILE.read_text(encoding="utf-8")
            if REPORTERS_FILE.exists()
            else "[]\n",
            ISSUES_FILE: ISSUES_FILE.read_text(encoding="utf-8")
            if ISSUES_FILE.exists()
            else "[]\n",
        }
        REPORTERS_FILE.write_text("[]\n", encoding="utf-8")
        ISSUES_FILE.write_text("[]\n", encoding="utf-8")

    def tearDown(self):
        for file_path, contents in self.original_contents.items():
            file_path.write_text(contents, encoding="utf-8")

    def post_json(self, url, payload):
        return self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_reporter_create_and_lookup(self):
        response = self.post_json(
            "/api/reporters/",
            {
                "id": 1,
                "name": "Asha Rao",
                "email": "asha@example.com",
                "team": "backend",
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["name"], "Asha Rao")

        list_response = self.client.get("/api/reporters/")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.json()), 1)

        lookup_response = self.client.get("/api/reporters/?id=1")
        self.assertEqual(lookup_response.status_code, 200)
        self.assertEqual(lookup_response.json()["id"], 1)

    def test_issue_create_uses_critical_subclass_message(self):
        response = self.post_json(
            "/api/issues/",
            {
                "id": 1,
                "title": "Login button not working on mobile",
                "description": "Users on iOS 17 cannot tap the login button",
                "status": "open",
                "priority": "critical",
                "reporter_id": 1,
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json()["message"],
            "[URGENT] Login button not working on mobile — needs immediate attention",
        )

        status_response = self.client.get("/api/issues/?status=open")
        self.assertEqual(status_response.status_code, 200)
        self.assertEqual(len(status_response.json()), 1)

    def test_low_priority_message_and_id_lookup(self):
        response = self.post_json(
            "/api/issues/",
            {
                "title": "Minor typo",
                "description": "Fix the label",
                "status": "open",
                "priority": "low",
                "reporter_id": 1,
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("low priority", response.json()["message"])

        issue_id = response.json()["id"]
        lookup_response = self.client.get(f"/api/issues/?id={issue_id}")
        self.assertEqual(lookup_response.status_code, 200)
        self.assertEqual(lookup_response.json()["id"], issue_id)

    def test_invalid_issue_and_missing_issue(self):
        response = self.post_json(
            "/api/issues/",
            {
                "title": "",
                "description": "Missing title",
                "status": "open",
                "priority": "high",
                "reporter_id": 1,
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Title cannot be empty")

        missing_response = self.client.get("/api/issues/?id=999")
        self.assertEqual(missing_response.status_code, 404)
        self.assertEqual(missing_response.json()["error"], "Issue not found")


if __name__ == "__main__":
    unittest.main()
