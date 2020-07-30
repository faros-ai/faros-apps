import app
import unittest

from faros.client import FarosClient
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class EC2UnusedSecurityGroupsTest(unittest.TestCase):
    def test_unused_security_groups(self, mock_execute):
        event = {"farosToken": "token"}
        data = {"aws": {"ec2": {"securityGroup": {"data": [
            {
                "farosAccountId": "farosAccountId",
                "farosRegionId": "farosRegionId",
                "groupId": "groupId1",
                "instances": {"data": []}
            },
            {
                "farosAccountId": "farosAccountId",
                "farosRegionId": "farosRegionId",
                "groupId": "groupId2",
                "instances": {"data": [
                    {"instanceId": "instanceId1"},
                    {"instanceId": "instanceId2"},
                ]}
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["groupId"], "groupId1")


if __name__ == "__main__":
    unittest.main()
