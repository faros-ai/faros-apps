import app
import unittest

from faros.client import FarosClient
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class EC2UnattachedEBSVolumesTest(unittest.TestCase):
    def test_can_filter_volumes(self, mock_client):
        event = {"farosToken": "token"}
        data = {"aws": {"ec2": {"volume": {"data": [
            {
                "farosAccountId": "farosAccountId",
                "farosRegionId": "farosRegionId",
                "volumeId": "vol-1",
                "state": "in-use",
                "instance": {"instanceId": "instanceId1"},
                "attachments": [
                    {"instanceId": "instanceId1"},
                    {"instanceId": "instanceId2"}
                ]
            },
            {
                "farosAccountId": "farosAccountId",
                "farosRegionId": "farosRegionId",
                "volumeId": "vol-4",
                "state": "available",
                "instance": {"instanceId": "instanceId2"},
                "attachments": [{"instanceId": "instanceId2"}]
            },
            {
                "farosAccountId": "farosAccountId",
                "farosRegionId": "farosRegionId",
                "volumeId": "vol-3",
                "state": "available",
                "instance": {"instanceId": "instanceId2"},
                "attachments": []
            },
            {
                "farosAccountId": "farosAccountId",
                "farosRegionId": "farosRegionId",
                "volumeId": "vol-2",
                "state": "available",
                "instance": {"instanceId": "instanceId2"},
                "attachments": None
            }
        ]}}}}

        mock_client.return_value = data
        results = app.lambda_handler(event, None)
        self.assertEqual(len(results), 2)
        unattached = {v["volumeId"] for v in results}
        self.assertSetEqual(unattached, {"vol-2", "vol-3"})
        mock_client.assert_called_once()


if __name__ == "__main__":
    unittest.main()
