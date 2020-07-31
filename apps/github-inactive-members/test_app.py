import app
import unittest

from datetime import datetime
from faros.client import FarosClient
from faros.utils import DATE_FORMAT
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class GitHubInactiveMembersTest(unittest.TestCase):
    def setUp(self):
        self.event = {"farosToken": "farosToken", "params": {"max_days": 60}}
        self.date = datetime.utcnow()

    def test_no_activity(self, mock_execute):
        data = {"github": {"user": {"data": [
            {
                "login": "login_name",
                "name": "name",
                "email": "name",
                "membership": "member",
                "commits": {"data": []},
                "issues": {"data": []},
                "pullRequests": {"data": []}
            }
        ]}}}

        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["login"], "login_name")

    def test_has_recent_activity(self, mock_execute):
        data = {"github": {"user": {"data": [
            {
                "login": "login_name",
                "name": "name",
                "email": "name",
                "membership": "member",
                "commits": {"data": [
                    {
                        "sha": "7fb4e",
                        "date": self.date.strftime(DATE_FORMAT)
                    }
                ]},
                "issues": {"data": []},
                "pullRequests": {"data": []}
            },
            {
                "login": "login_name56",
                "name": "name",
                "email": "name",
                "membership": "member",
                "commits": {"data": []},
                "issues": {"data": []},
                "pullRequests": {"data": [
                    {
                        "state": "closed",
                        "updated_at": self.date.strftime(DATE_FORMAT)
                    }
                ]}
            },
            {
                "login": "login_name4",
                "name": "name",
                "email": "name",
                "membership": "member",
                "commits": {"data": []},
                "issues": {"data": [
                    {
                        "state": "open",
                        "updated_at": self.date.strftime(DATE_FORMAT)
                    }
                ]},
                "pullRequests": {"data": []}
            }
        ]}}}

        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertFalse(results)

    def test_activity_is_past_max_days(self, mock_execute):
        data = {"github": {"user": {"data": [
            {
                "login": "login",
                "name": "name",
                "email": "name",
                "membership": "member",
                "commits": {"data": [
                    {
                        "sha": "7fb4e",
                        "date": "2020-03-20T00:04:01Z"
                    }
                ]},
                "issues": {"data": []},
                "pullRequests": {"data": []}
            },
            {
                "login": "login56",
                "name": "name",
                "email": "name",
                "membership": "member",
                "commits": {"data": []},
                "issues": {"data": []},
                "pullRequests": {"data": [
                    {
                        "state": "closed",
                        "updated_at": "2019-07-28T08:34:26Z"
                    }
                ]}
            },
            {
                "login": "login4",
                "name": "name",
                "email": "name",
                "membership": "member",
                "commits": {"data": []},
                "issues": {"data": [
                    {
                        "state": "open",
                        "updated_at": "2019-07-25T07:07:26Z"
                    }
                ]},
                "pullRequests": {"data": []}
            }
        ]}}}

        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(results), 3)
        logins = {u["login"] for u in results}
        self.assertSetEqual(logins, {"login56", "login4", "login"})

    def test_no_max_days_param(self, mock_execute):
        event = {"farosToken": "farosToken", "params": {"other": 90}}
        with self.assertRaises(KeyError):
            app.lambda_handler(event, None)
        self.assertFalse(mock_execute.called)


if __name__ == "__main__":
    unittest.main()
