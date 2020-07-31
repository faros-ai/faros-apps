import app
import json
import unittest

from faros.client import FarosClient
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class S3MissingBucketPolicyTest(unittest.TestCase):
    def setUp(self):
        self.event = {
            "farosToken": "token",
            "params": {
                "required_policy_statement": "DenyUploads,AllowUnEncrypted"
            }
        }

    def test_bucket_no_policy(self, mock_execute):
        data = {"aws": {"s3": {"bucket": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "name": "bucket1",
                "policy": None
            }
        ]}}}}

        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(results), 1)
        required = {"DenyUploads", "AllowUnEncrypted"}
        missing = frozenset(results[0]["missingPolicies"])
        self.assertSetEqual(missing, required)

    def test_bucket_has_no_policy(self, mock_execute):
        policy = json.dumps({
            "Version": "2008-10-17",
            "Id": "Policy1425281770533",
            "Statement": [
                {
                    "Sid": "AllowUser",
                    "Effect": "Allow",
                    "Resource": "arn:aws"
                }
            ]
        })
        data = {"aws": {"s3": {"bucket": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "name": "bucket1",
                "policy": {"policy": policy}
            }
        ]}}}}

        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(results), 1)
        required = {"DenyUploads", "AllowUnEncrypted"}
        missing = frozenset(results[0]["missingPolicies"])
        self.assertSetEqual(missing, required)

    def test_missing_single_policy(self, mock_execute):
        policy = json.dumps({
            "Version": "2008-10-17",
            "Id": "Policy1425281770533",
            "Statement": [
                {
                    "Sid": "AllowUnEncrypted",
                    "Effect": "Allow",
                    "Resource": "arn:aws"
                }
            ]
        })
        data = {"aws": {"s3": {"bucket": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "name": "bucket1",
                "policy": {"policy": policy}
            }
        ]}}}}

        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(results), 1)
        missing = frozenset(results[0]["missingPolicies"])
        self.assertSetEqual(missing, {"DenyUploads"})

    def test_bucket_has_policies(self, mock_execute):
        policy = json.dumps({
            "Version": "2008-10-17",
            "Id": "Policy1425281770533",
            "Statement": [
                {
                    "Sid": "AllowUnEncrypted",
                    "Effect": "Allow",
                    "Resource": "arn:aws"
                },
                {
                    "Sid": "DenyUploads",
                    "Effect": "Allow",
                    "Resource": "arn:aws"
                }
            ]
        })
        data = {"aws": {"s3": {"bucket": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "name": "bucket1",
                "policy": {"policy": policy}
            }
        ]}}}}

        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertFalse(results)

    def test_required_policies_not_defined(self, mock_execute):
        event = {"farosToken": "token"}
        mock_execute.return_value = None
        with self.assertRaises(KeyError):
            app.lambda_handler(event, None)
        self.assertFalse(mock_execute.called)


if __name__ == "__main__":
    unittest.main()
