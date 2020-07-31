import app
import unittest

from faros.client import FarosClient
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class GitHubOpenUnassignedIssuesTest(unittest.TestCase):
    def setUp(self):
        self.event = {"farosToken": "farosToken"}

    def test_closed_issue(self, mock_execute):
        data = {"github": {"issue": {"data": [
            {
                "number": 67,
                "title": "pr title",
                "state": "closed",
                "repo_name": "poseidon",
                "created_at": "2020-07-20T16:49:44Z",
                "comments": 0,
                "assignee_login": None,
                "pull_request": None
            }
        ]}}}

        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertFalse(results)

    def test_open_issue_with_assignee(self, mock_execute):
        data = {"github": {"issue": {"data": [
            {
                "number": 7,
                "title": "pr title",
                "state": "open",
                "repo_name": "poseidon",
                "created_at": "2020-05-29T19:07:26Z",
                "comments": 0,
                "assignee_login": "user546",
                "pull_request": None
            },
            {
                "number": 99,
                "title": "pr title",
                "state": "open",
                "repo_name": "poseidon",
                "created_at": "2020-05-29T19:07:26Z",
                "comments": 0,
                "assignee_login": None,
                "pull_request": None
            }
        ]}}}

        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["number"], 99)


if __name__ == "__main__":
    unittest.main()
