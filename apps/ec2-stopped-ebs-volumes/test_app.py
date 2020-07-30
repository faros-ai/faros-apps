import app
import unittest

from faros.client import FarosClient
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class Ec2EbsStoppedVolumesTest(unittest.TestCase):
    def setUp(self):
        self.event = {"farosToken": "token"}

    def test_gets_stopped_volumes(self, mock_client):
        data = {"aws": {"ec2": {"volume": {"data": [
            {
                "farosAccountId": "farosAccountId",
                "farosRegionId": "farosRegionId",
                "volumeId": "vol-1",
                "state": "in-use",
                "instance": {
                    "instanceId": "instanceId1",
                    "state": {"name": "running"}
                }
            },
            {
                "farosAccountId": "farosAccountId",
                "farosRegionId": "farosRegionId",
                "volumeId": "vol-2",
                "state": "available",
                "instance": {
                    "instanceId": "instanceId1",
                    "state": {"name": "stopped"}
                }
            }
        ]}}}}

        mock_client.return_value = data
        results = app.lambda_handler(self.event, None)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["volumeId"], "vol-2")
        mock_client.assert_called_once()

    def test_handle_no_instance(self, mock_client):
        data = {"aws": {"ec2": {"volume": {"data": [
            {
                "farosAccountId": "farosAccountId",
                "farosRegionId": "farosRegionId",
                "volumeId": "vol-1",
                "state": "in-use",
                "instance": None
            }
        ]}}}}

        mock_client.return_value = data
        results = app.lambda_handler(self.event, None)
        self.assertFalse(results)
        mock_client.assert_called_once()


if __name__ == "__main__":
    unittest.main()
