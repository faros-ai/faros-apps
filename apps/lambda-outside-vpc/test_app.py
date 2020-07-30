import app
import unittest

from faros.client import FarosClient
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class LambdaOutsideVPCTest(unittest.TestCase):
    def setUp(self):
        self.event = {"farosToken": "token"}

    def test_no_vpc_config(self, mock_execute):
        data = {"aws": {"lambda": {"functionConfiguration": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "functionName": "func1",
                "functionArn": "arn:aws:func1",
                "vpcConfig": None
            }
        ]}}}}

        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(results), 1)

    def test_no_vpc_subnets(self, mock_execute):
        data = {"aws": {"lambda": {"functionConfiguration": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "functionName": "func1",
                "functionArn": "arn:aws:func1",
                "vpcConfig": {"subnetIds": []}
            }
        ]}}}}

        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(results), 1)

    def test_lambda_has_subnets(self, mock_execute):
        data = {"aws": {"lambda": {"functionConfiguration": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "functionName": "func1",
                "functionArn": "arn:aws:func1",
                "vpcConfig": {"subnetIds": [
                    {"subnetIds": "subnetIds1"},
                    {"subnetIds": "subnetIds2"}
                ]}
            }
        ]}}}}

        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertFalse(results)


if __name__ == "__main__":
    unittest.main()
