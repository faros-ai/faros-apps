import app
import unittest

from datetime import datetime
from faros.client import FarosClient
from faros.utils import DATE_FORMAT
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class GitHubOldPullRequestsTest(unittest.TestCase):
    def setUp(self):
        self.event = {"farosToken": "farosToken", "params": {"max_days": 60}}
        self.date = datetime.utcnow()

    def test_closed_pr(self, mock_execute):
        data = {"github": {"pullRequest": {"data": [
            {
                "number": 67,
                "title": "pr title",
                "state": "closed",
                "repo_name": "poseidon",
                "created_at": "2020-06-18T22:45:01Z",
                "user_login": "user",
            }
        ]}}}

        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertFalse(results)

    def test_pr_has_recent_activity(self, mock_execute):
        data = {"github": {"pullRequest": {"data": [
            {
                "number": 67,
                "title": "pr title",
                "state": "open",
                "repo_name": "poseidon",
                "created_at": self.date.strftime(DATE_FORMAT),
                "user_login": "user",
            }
        ]}}}

        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertFalse(results)

    def test_pr_past_max_days(self, mock_execute):
        data = {"github": {"pullRequest": {"data": [
            {
                "number": 670,
                "title": "pr title",
                "state": "open",
                "repo_name": "poseidon",
                "created_at": "2019-07-28T09:07:26Z",
                "user_login": "user",
            }
        ]}}}

        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["number"], 670)

    def test_no_max_days_param(self, mock_execute):
        event = {"farosToken": "farosToken", "params": {"other": 90}}
        with self.assertRaises(KeyError):
            app.lambda_handler(event, None)
        self.assertFalse(mock_execute.called)


if __name__ == "__main__":
    unittest.main()
