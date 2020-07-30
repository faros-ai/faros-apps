import app
import unittest

from faros.client import FarosClient
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class EC2PublicInstancesTest(unittest.TestCase):
    def test_get_public_instances(self, mocked_execute):
        data = {"aws": {"ec2": {"instance": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "instanceId": "instanceId1",
                "publicIpAddress": "publicIpAddress"
            },
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "instanceId": "instanceId2",
                "publicIpAddress": None
            },
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "instanceId": "instanceId3",
                "publicIpAddress": "publicIpAddress2"
            }
            ]}}}
        }

        mocked_execute.return_value = data
        event = {"farosToken": "token"}
        results = app.lambda_handler(event, None)
        mocked_execute.assert_called_once()
        self.assertEqual(len(results), 2)


if __name__ == "__main__":
    unittest.main()
