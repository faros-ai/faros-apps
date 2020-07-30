import app
import unittest

from datetime import datetime
from faros.client import FarosClient
from faros.utils import DATE_FORMAT
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class IAMInactiveUsersTest(unittest.TestCase):
    def setUp(self):
        self.event = {"farosToken": "farosToken", "params": {"max_days": 90}}

    def test_user_is_active(self, mock_execute):
        data = {"aws": {"iam": {"user": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "userId": "HephaestusId",
                "userName": "Hephaestus",
                "passwordLastUsed": datetime.utcnow().strftime(DATE_FORMAT)
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertFalse(results)

    def test_user_inactive(self, mock_execute):
        data = {"aws": {"iam": {"user": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "userId": "HephaestusId",
                "userName": "Hephaestus",
                "passwordLastUsed": "2020-03-25T22:07:15Z"
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["userId"], "HephaestusId")

    def test_no_max_days_param(self, mock_execute):
        event = {"farosToken": "farosToken", "params": {}}
        with self.assertRaises(KeyError):
            app.lambda_handler(event, None)
        self.assertFalse(mock_execute.called)

    def test_invalid_max_days_param(self, mock_execute):
        event = {"farosToken": "farosToken", "params": {"max_days": 0}}
        with self.assertRaises(ValueError):
            app.lambda_handler(event, None)
        self.assertFalse(mock_execute.called)


if __name__ == "__main__":
    unittest.main()
