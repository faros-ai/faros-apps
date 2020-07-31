import app
import unittest

from faros.client import FarosClient
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class S3UnencryptedBucketTest(unittest.TestCase):
    def test_bucket_unencrypted(self, mock_execute):
        event = {"farosToken": "token"}
        data = {"aws": {"s3": {"bucket": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "name": "bucket2",
                "encryption": None
            },
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "name": "bucket1",
                "encryption": {
                    "rules": [
                        {
                            "applyServerSideEncryptionByDefault": {
                                "kmsMasterKeyID": None,
                                "sseAlgorithm": "sseAlgorithm"
                            }
                        }
                    ]
                }
            }
        ]}}}}

        mock_execute.return_value = data
        results = app.lambda_handler(event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "bucket2")


if __name__ == "__main__":
    unittest.main()
