import app
import unittest

from faros.client import FarosClient
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class EC2UnattachedEgressOnlyTest(unittest.TestCase):
    def test_can_filter_gateways(self, mock_execute):
        event = {"farosToken": "token"}
        data = {"aws": {"ec2": {"egressOnlyInternetGateway": {"data": [
            {
                "farosAccountId": "farosAccountId",
                "farosRegionId": "farosRegionId",
                "egressOnlyInternetGatewayId": "gateway1",
                "attachments": None
            },
            {
                "farosAccountId": "farosAccountId",
                "farosRegionId": "farosRegionId",
                "egressOnlyInternetGatewayId": "gateway2",
                "attachments": [
                    {"vpcId": "vpcId1"},
                    {"vpcId": "vpcId"}
                ]
            },
            {
                "farosAccountId": "farosAccountId",
                "farosRegionId": "farosRegionId",
                "egressOnlyInternetGatewayId": "gateway3",
                "attachments": []
            }
        ]}}}}

        mock_execute.return_value = data
        result = app.lambda_handler(event, None)
        self.assertEqual(len(result), 2)
        unattached = {g["egressOnlyInternetGatewayId"] for g in result}
        self.assertSetEqual(unattached, {"gateway3", "gateway1"})
        mock_execute.assert_called_once()


if __name__ == "__main__":
    unittest.main()
