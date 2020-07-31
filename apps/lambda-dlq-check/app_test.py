import app
import unittest

from faros.client import FarosClient
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class LambdaDQLCheckTest(unittest.TestCase):
    def setUp(self):
        self.event = {"farosToken": "token"}

    def test_no_deadletter_config(self, mock_execute):
        data = {"aws": {"lambda": {"functionConfiguration": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "functionName": "func1",
                "functionArn": "arn:aws:func1",
                "deadLetterConfig": {"targetArn": None}
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(results), 1)

    def test_has_deadletter_config(self, mock_execute):
        data = {"aws": {"lambda": {"functionConfiguration": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "functionName": "func1",
                "functionArn": "arn:aws:func1",
                "deadLetterConfig": {"targetArn": "arn:aws"}
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertFalse(results)


if __name__ == "__main__":
    unittest.main()
