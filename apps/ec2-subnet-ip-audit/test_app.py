import app
import unittest

from faros.client import FarosClient
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class Ec2SubnetIpAudit(unittest.TestCase):
    def setUp(self):
        self.event = {
            "farosToken": "token",
            "params": {"ip_count": 500}
        }

        self.data = {"aws": {"ec2": {"subnet": {"data": [
            {
              "farosAccountId": "farosAccountId",
              "farosRegionId": "farosRegionId",
              "subnetId": "subnet-1",
              "availableIpAddressCount": 249
            },
            {
              "farosAccountId": "farosAccountId",
              "farosRegionId": "farosRegionId",
              "subnetId": "subnet-2",
              "availableIpAddressCount": 4091
            },
            {
              "farosAccountId": "farosAccountId",
              "farosRegionId": "farosRegionId",
              "subnetId": "subnet-3",
              "availableIpAddressCount": 0
            }
        ]}}}}

    def test_filter_subnets(self, mock_client):
        mock_client.return_value = self.data

        results = app.lambda_handler(self.event, None)
        self.assertEqual(len(results), 2)
        ids = {s["subnetId"] for s in results}
        self.assertSetEqual(ids, {"subnet-1", "subnet-3"})
        mock_client.assert_called_once()

    def test_missing_param(self, mock_client):
        mock_client.return_value = self.data
        event = {"farosToken": "token", "params": {}}

        with self.assertRaises(KeyError) as ex:
            app.lambda_handler(event, None)
        self.assertFalse(mock_client.called)
        self.assertEqual("'ip_count'", str(ex.exception))

    def test_invalid_ipcount(self, mock_client):
        event = {
            "farosToken": "token",
            "params": {"ip_count": -5}
        }
        mock_client.return_value = self.data
        with self.assertRaises(ValueError) as ex:
            app.lambda_handler(event, None)
        self.assertFalse(mock_client.called)
        self.assertEqual("IP count should be a positive integer",
                         str(ex.exception))


if __name__ == "__main__":
    unittest.main()
