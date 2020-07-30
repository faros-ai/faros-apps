import app
import unittest

from datetime import datetime, timedelta
from faros.client import FarosClient
from faros.utils import DATE_FORMAT
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class ACMExpiringCertificatesTest(unittest.TestCase):
    def setUp(self):
        self.event = {"farosToken": "farosToken", "params": {"days_left": 100}}
        self.date = datetime.utcnow()

    def test_certificate_expired(self, mock_execute):
        expired_date = (self.date - timedelta(days=100)).strftime(DATE_FORMAT)
        query_data = {"aws": {"acm": {"certificateDetail": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "us-east-2",
                "certificateArn": "arn:certificateArn2",
                "notAfter": expired_date
            }
        ]}}}}
        mock_execute.return_value = query_data
        results = app.lambda_handler(self.event, None)
        self.assertEqual(len(results), 1)
        mock_execute.assert_called_once()

    def test_certificate_expiring(self, mock_execute):
        to_expire = (self.date + timedelta(days=30)).strftime(DATE_FORMAT)
        query_data = {"aws": {"acm": {"certificateDetail": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosRegionId",
                "certificateArn": "arn:certificateArn",
                "notAfter": to_expire
            }
        ]}}}}
        mock_execute.return_value = query_data
        results = app.lambda_handler(self.event, None)
        self.assertEqual(len(results), 1)
        mock_execute.assert_called_once()

    def test_certificate_not_expired(self, mock_execute):
        not_expired = (self.date + timedelta(days=365)).strftime(DATE_FORMAT)
        query_data = {"aws": {"acm": {"certificateDetail": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosRegionId",
                "certificateArn": "arn:certificateArn",
                "notAfter": not_expired
            }
        ]}}}}
        mock_execute.return_value = query_data
        results = app.lambda_handler(self.event, None)
        self.assertFalse(results)
        mock_execute.assert_called_once()

    def test_exception_when_no_days_left_param(self, mock_execute):
        event = {"farosToken": "farosToken"}
        with self.assertRaises(KeyError):
            app.lambda_handler(event, None)
        self.assertFalse(mock_execute.called)

    def test_exception_when_invalid_days_left_param(self, mock_execute):
        event = {"farosToken": "farosToken", "params": {"days_left": -3}}
        with self.assertRaises(ValueError):
            app.lambda_handler(event, None)
        self.assertFalse(mock_execute.called)


if __name__ == "__main__":
    unittest.main()
