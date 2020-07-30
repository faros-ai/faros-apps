import app
import unittest

from faros.client import FarosClient
from unittest.mock import patch


@patch.object(FarosClient, 'graphql_execute')
class Ec2RunningInfraWithTagTest(unittest.TestCase):
    def test_get_infra_with_tag(self, mock_client):
        event = {
            "farosToken": "token",
            "params": {"tag_name": "tag1", "tag_value": "1"}
        }
        data = {"aws": {"ec2": {"instance": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "instanceId": "instanceId",
                "instanceType": "t2.micro",
                "tags": [{"key": "tag1", "value": "1"}],
                "state": {"name": "running"},
                "volumes": {
                    "data": [
                        {"size": 8, "volumeType": "gp2"}
                    ]
                }
            },
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "instanceId": "instanceId1",
                "instanceType": "t2.micro",
                "tags": [{"key": "tag2", "value": "2"}],
                "state": {"name": "running"},
                "volumes": {
                    "data": [
                        {"size": 8, "volumeType": "gp3"}
                    ]
                }
            },
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "instanceId": "instanceId",
                "instanceType": "t2.micro",
                "tags": [
                    {"key": "tag1", "value": "1"},
                    {"key": "tag2", "value": "2"}
                ],
                "state": {"name": "stopped"},
                "volumes": {
                    "data": [
                        {"size": 8, "volumeType": "gp2"}
                    ]
                }
            },
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "instanceId": "instanceId",
                "instanceType": "t2.micro",
                "tags": [
                    {"key": "tag1", "value": "2"},
                    {"key": "tag2", "value": "2"}
                ],
                "state": {"name": "stopped"},
                "volumes": {
                    "data": [
                        {"size": 8, "volumeType": "gp2"}
                    ]
                }
            }
        ]}}}}

        mock_client.return_value = data
        results = app.lambda_handler(event, None)
        self.assertTrue(mock_client.called_oncce)
        self.assertEqual(len(results), 1)

    def test_missing_tag_value(self, mock_client):
        event = {
            "farosToken": "token",
            "params": {"tag_name": "tag1"}
        }
        mock_client.return_value = {}

        with self.assertRaises(KeyError) as ex:
            app.lambda_handler(event, None)
        self.assertEqual("'tag_value'", str(ex.exception))
        self.assertFalse(mock_client.called)

    def test_missing_tag_key(self, mock_client):
        event = {
            "farosToken": "token",
            "params": {"tag_value": "1"}
        }
        mock_client.return_value = {}

        with self.assertRaises(KeyError) as ex:
            app.lambda_handler(event, None)
        self.assertEqual("'tag_name'", str(ex.exception))
        self.assertFalse(mock_client.called)


if __name__ == "__main__":
    unittest.main()
