import app
import unittest

from faros.client import FarosClient
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class EC2VPCWithoutS3EnabledTest(unittest.TestCase):
    def setUp(self):
        self.event = {"farosToken": "token"}

    def test_no_vpcs(self, mock_execute):
        data = {"aws": {"ec2": {"vpc": {"data": []}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        self.assertFalse(results)
        mock_execute.assert_called_once()

    def test_no_vpcendpoints(self, mock_execute):
        data = {"aws": {"ec2": {"vpc": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "vpcId": "vpcId",
                "vpcEndpoints": {"data": []}
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        self.assertEqual(len(results), 1)
        mock_execute.assert_called_once()

    def test_vpcendpoints_state_unavailable(self, mock_execute):
        data = {"aws": {"ec2": {"vpc": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "vpcId": "vpcId",
                "vpcEndpoints": {"data": [
                    {
                        "state": "pending",
                        "serviceName": "com.amazonaws.us-east-1.s3",
                        "vpcEndpointId": "vpcEndpointId1"
                    }
                ]}
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        self.assertEqual(len(results), 1)
        mock_execute.assert_called_once()

    def test_s3_service_not_enabled(self, mock_execute):
        data = {"aws": {"ec2": {"vpc": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "vpcId": "vpcId",
                "vpcEndpoints": {"data": [
                    {
                        "state": "available",
                        "serviceName": "com.amazonaws.us-east-1.dynamodb",
                        "vpcEndpointId": "vpcEndpointId1"
                    },
                    {
                        "state": "available",
                        "serviceName": "com.amazonaws.us-east-1.elasticcache",
                        "vpcEndpointId": "vpcEndpointId2"
                    }
                ]}
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        self.assertEqual(len(results), 1)
        mock_execute.assert_called_once()

    def test_s3_service_available(self, mock_execute):
        data = {"aws": {"ec2": {"vpc": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "vpcId": "vpcId",
                "vpcEndpoints": {"data": [
                    {
                        "state": "available",
                        "serviceName": "com.amazonaws.us-east-1.dynamodb",
                        "vpcEndpointId": "vpcEndpointId1"
                    },
                    {
                        "state": "available",
                        "serviceName": "com.amazonaws.us-east-1.s3",
                        "vpcEndpointId": "vpcEndpointId2"
                    }
                ]}
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        self.assertFalse(results)
        mock_execute.assert_called_once()


if __name__ == "__main__":
    unittest.main()
