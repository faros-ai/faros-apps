import app
import unittest

from faros.client import FarosClient
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class S3BucketPublicAccessAuditTest(unittest.TestCase):
    def setUp(self):
        self.event = {"farosToken": "token"}

    def test_policy_public_block_not_defined(self, mock_execute):
        data = {"aws": {"s3": {"bucket": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "name": "bucket1",
                "policyStatus": None,
                "publicAccessBlock": None
            }
        ]}}}}

        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertFalse(results)

    def test_policy_status_enabled(self, mock_execute):
        data = {"aws": {"s3": {"bucket": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "name": "bucket1",
                "policyStatus": {
                    "isPublic": True
                },
                "publicAccessBlock": None
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.called_once()
        self.assertEqual(len(results), 1)

    def test_policy_all_disabled(self, mock_execute):
        data = {"aws": {"s3": {"bucket": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "name": "bucket1",
                "policyStatus": {
                    "isPublic": False
                },
                "publicAccessBlock": {
                    "blockPublicAcls": True,
                    "blockPublicPolicy": True,
                    "ignorePublicAcls": True,
                    "restrictPublicBuckets": True
                }
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.called_once()
        self.assertFalse(results)

    def test_block_has_at_least_one_enabled(self, mock_execute):
        data = {"aws": {"s3": {"bucket": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "name": "bucket1",
                "policyStatus": {
                    "isPublic": False
                },
                "publicAccessBlock": {
                    "blockPublicAcls": True,
                    "blockPublicPolicy": False,
                    "ignorePublicAcls": True,
                    "restrictPublicBuckets": True
                }
            },
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "name": "bucket2",
                "policyStatus": {
                    "isPublic": False
                },
                "publicAccessBlock": {
                    "blockPublicAcls": True,
                    "blockPublicPolicy": True,
                    "ignorePublicAcls": False,
                    "restrictPublicBuckets": True
                }
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.called_once()
        self.assertEqual(len(results), 2)
        public = {b["name"] for b in results}
        self.assertSetEqual(public, {"bucket1", "bucket2"})


if __name__ == "__main__":
    unittest.main()
