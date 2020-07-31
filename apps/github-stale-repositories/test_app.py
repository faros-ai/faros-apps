import app
import unittest

from datetime import datetime, timedelta
from faros.client import FarosClient
from faros.utils import DATE_FORMAT
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class GitHubStaleRepositoriesTest(unittest.TestCase):
    def setUp(self):
        self.event = {"farosToken": "farosToken", "params": {"max_days": 200}}

    def test_stale_repo(self, mock_execute):
        data = {"github": {"repository": {"data": [
            {
                "name": "repo1",
                "created_at": "2020-07-09T03:11:05Z",
                "updated_at": "2019-07-09T03:11:08Z"
            },
            {
                "name": "repo2",
                "created_at": "2020-03-25T22:07:15Z",
                "updated_at": "2019-06-04T02:39:28Z"
            }
        ]}}}

        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(results), 2)
        names = {b["name"] for b in results}
        self.assertEqual(names, {"repo1", "repo2"})

    def test_recent_update(self, mock_execute):
        date = datetime.utcnow()
        date2 = (date - timedelta(days=150)).strftime(DATE_FORMAT)
        data = {"github": {"repository": {"data": [
            {
                "name": "repo1",
                "created_at": "2020-07-09T03:11:05Z",
                "updated_at": date.strftime(DATE_FORMAT)
            },
            {
                "name": "repo2",
                "created_at": "2020-03-25T22:07:15Z",
                "updated_at": date2
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
