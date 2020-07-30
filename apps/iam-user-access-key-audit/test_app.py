import app
import unittest

from datetime import datetime, timedelta
from faros.client import FarosClient
from faros.utils import DATE_FORMAT
from unittest.mock import patch


class IAMUserAccessKeyAuditTest(unittest.TestCase):
    def setUp(self):
        self.event = {"farosToken": "farosToken", "params": {"max_days": 90}}
        self.date = (datetime.utcnow() -
                     timedelta(days=47)).strftime(DATE_FORMAT)

    @patch.object(FarosClient, "graphql_execute")
    def test_user_no_keys(self, mock_execute):
        data = {"aws": {"iam": {"userDetail": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "userId": "HephaestusId",
                "userName": "Hephaestus",
                "accessKeys": {"data": []}
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertFalse(results)

    @patch.object(FarosClient, "graphql_execute")
    def test_user_key_not_active(self, mock_execute):
        data = {"aws": {"iam": {"userDetail": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "userId": "HephaestusId",
                "userName": "Hephaestus",
                "accessKeys": {
                    "data": [
                        {
                            "status": "Inactive",
                            "createDate": "2020-07-21T20:46:26Z",
                            "accessKeyId": "keyId"
                        }
                    ]
                }
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertFalse(results)

    @patch.object(FarosClient, "graphql_execute")
    def test_user_key_recent(self, mock_execute):
        data = {"aws": {"iam": {"userDetail": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "userId": "HephaestusId",
                "userName": "Hephaestus",
                "accessKeys": {
                    "data": [
                        {
                            "status": "Active",
                            "createDate": self.date,
                            "accessKeyId": "keyId"
                        }
                    ]
                }
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertFalse(results)

    @patch.object(FarosClient, "graphql_execute")
    def test_user_key_not_recent(self, mock_execute):
        data = {"aws": {"iam": {"userDetail": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "userId": "HephaestusIdOldKeys",
                "userName": "Hephaestus",
                "accessKeys": {
                    "data": [
                        {
                            "status": "Active",
                            "createDate": "2020-01-20T20:31:00Z",
                            "accessKeyId": "OldkeyId"
                        },
                        {
                            "status": "Active",
                            "createDate": self.date,
                            "accessKeyId": "keyId"
                        }
                    ]
                }
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["userId"], "HephaestusIdOldKeys")
        self.assertEqual(len(results[0]["accessKeys"]), 1)
        expired = {k["accessKeyId"] for u in results for k in u["accessKeys"]}
        self.assertSetEqual(expired, {"OldkeyId"})

    @patch.object(FarosClient, "graphql_execute")
    def test_no_max_days_param(self, mock_execute):
        event = {"farosToken": "farosToken", "params": {}}
        with self.assertRaises(KeyError):
            app.lambda_handler(event, None)
        self.assertFalse(mock_execute.called)

    @patch.object(FarosClient, "graphql_execute")
    def test_invalid_max_days_param(self, mock_execute):
        event = {"farosToken": "farosToken", "params": {"max_days": 0}}
        with self.assertRaises(ValueError):
            app.lambda_handler(event, None)
        self.assertFalse(mock_execute.called)


if __name__ == "__main__":
    unittest.main()
