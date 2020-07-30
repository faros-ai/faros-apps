import app
import json
import unittest

from faros.client import FarosClient
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class Ec2ExposedVPCEndpointsTest(unittest.TestCase):
    def setUp(self):
        self.event = {"farosToken": "farosToken"}

    def test_gets_exposed_vpcs(self, mock_execute):
        exposed = {
            "Version": "2008-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "*",
                    "Resource": "*"
                    }
            ]
        }

        secure = {
            "Version": "2008-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "test_arn",
                    "Action": "*",
                    "Resource": "*"
                    }
            ]
        }

        data = {"aws": {"ec2": {"vpcEndpoint": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "vpcId": "vpcId",
                "policyDocument": json.dumps(exposed)
            },
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "vpcId": "vpcId2",
                "policyDocument": json.dumps(secure)
            }
            ]}}}
        }

        mock_execute.return_value = data
        result = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["vpcId"], "vpcId")


if __name__ == '__main__':
    unittest.main()
