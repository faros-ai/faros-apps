import app
import unittest

from datetime import datetime, timedelta
from faros.client import FarosClient
from faros.utils import DATE_FORMAT
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class GitHubStaleBranchesTest(unittest.TestCase):
    def setUp(self):
        self.event = {"farosToken": "farosToken", "params": {"max_days": 60}}

    def test_stale_branch(self, mock_execute):
        data = {"github": {"repository": {"data": [
            {
                "branches": {"data": [
                    {
                        "name": "master",
                        "repo_name": "repo1",
                        "commit_sha": "81c4",
                        "protected": False,
                        "commit": {
                            "sha": "81c4",
                            "date": "2020-04-30T05:39:28Z"
                        }
                    },
                    {
                        "name": "test_branch",
                        "repo_name": "repo2",
                        "commit_sha": "81c4",
                        "protected": True,
                        "commit": {
                            "sha": "81c4",
                            "date": "2019-04-01T05:39:28Z"
                        }
                    }
                ]}
            }
        ]}}}

        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(results), 2)
        names = {b["name"] for b in results}
        self.assertEqual(names, {"master", "test_branch"})

    def test_branch_commit_recent(self, mock_execute):
        date = datetime.utcnow()
        date2 = (date - timedelta(hours=10)).strftime(DATE_FORMAT)
        data = {"github": {"repository": {"data": [
            {
                "branches": {"data": [
                    {
                        "name": "master",
                        "repo_name": "repo1",
                        "commit_sha": "81c4",
                        "protected": False,
                        "commit": {
                            "sha": "81c4",
                            "date": date.strftime(DATE_FORMAT),
                        }
                    },
                    {
                        "name": "test_branch",
                        "repo_name": "repo2",
                        "commit_sha": "81c4",
                        "protected": True,
                        "commit": {
                            "sha": "8154",
                            "date": date2
                        }
                    }
                ]}
            }
        ]}}}

        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertFalse(results)

    def test_no_max_days_param(self, mock_execute):
        event = {"farosToken": "farosToken", "params": {"other": 90}}
        with self.assertRaises(KeyError):
            app.lambda_handler(event, None)
        self.assertFalse(mock_execute.called)


if __name__ == "__main__":
    unittest.main()
