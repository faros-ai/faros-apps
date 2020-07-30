import app
import unittest

from faros.client import FarosClient
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class Ec2UnattachedVPCGatewayTest(unittest.TestCase):
    def test_unattached_vpc(self, mock_execute):
        event = {"farosToken": "token"}
        data = {"aws": {"ec2": {"internetGateway": {"data": [
            {
                "farosAccountId": "farosAccountId",
                "farosRegionId": "farosRegionId",
                "internetGatewayId": "internetGatewayId",
                "attachments": [{"vpcId": "vpcId1"}]
            },
            {
                "farosAccountId": "farosAccountId",
                "farosRegionId": "farosRegionId",
                "internetGatewayId": "internetGatewayId2",
                "attachments": []
            },
            {
                "farosAccountId": "farosAccountId",
                "farosRegionId": "farosRegionId",
                "internetGatewayId": "internetGatewayId3",
                "attachments": [
                    {"vpcId": "vpcId2"},
                    {"vpcId": "vpcId1"}
                ]
            }
        ]}}}}

        mock_execute.return_value = data
        results = app.lambda_handler(event, None)
        self.assertEqual(len(results), 1)
        unattached = {u["internetGatewayId"] for u in results}
        self.assertSetEqual(unattached, {"internetGatewayId2"})


if __name__ == "__main__":
    unittest.main()