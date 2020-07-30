import app
import unittest

from faros.client import FarosClient
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class EC2MissingInstanceTagsTest(unittest.TestCase):
    def setUp(self):
        self.event = {
            "farosToken": "farosToken",
            "params": {"keys": "tag1,tag2"}
        }

    def test_missing_tags(self, mocked_execute):
        data = {"aws": {"ec2": {"instance": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "instanceId": "instanceId1",
                "tags": [{"key": "tag1", "value": "1"}],
            }
        ]}}}}

        mocked_execute.return_value = data
        result = app.lambda_handler(self.event, None)
        mocked_execute.assert_called_once()
        self.assertEqual(len(result), 1)

    def test_no_missing_tags(self, mocked_execute):
        data = {"aws": {"ec2": {"instance": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "instanceId": "instanceId1",
                "tags": [
                    {"key": "tag1", "value": "1"},
                    {"key": "tag2", "value": "2"}
                ],
            }
        ]}}}}

        mocked_execute.return_value = data
        result = app.lambda_handler(self.event, None)
        self.assertFalse(result)
        mocked_execute.assert_called_once()

    def test_missing_param(self, mocked_execute):
        event = {"farosToken": "token"}
        mocked_execute.return_value = None
        with self.assertRaises(KeyError):
            app.lambda_handler(event, None)
        self.assertFalse(mocked_execute.called)


if __name__ == "__main__":
    unittest.main()
