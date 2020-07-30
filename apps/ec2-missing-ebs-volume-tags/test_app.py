import app
import unittest

from faros.client import FarosClient
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class EC2MissingEBSVolumeTagsTest(unittest.TestCase):
    def setUp(self):
        self.event = {"farosToken": "farosToken"}

    def test_missing_tags(self, mock_execute):
        data = {"aws": {"ec2": {"volume": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "volumeId": "volumeId",
                "tags": [{"key": "tag1", "value": "1"}],
                "state": "in-use",
                "instance": {
                    "tags": [
                        {"key": "tag1", "value": "1"},
                        {"key": "tag2", "value": "2"}
                    ]
                }
            },
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "volumeId": "volumeId",
                "tags": [],
                "state": "in-use",
                "instance": {
                    "tags": [
                        {"key": "tag1", "value": "1"},
                        {"key": "tag2", "value": "2"}
                    ]
                }
            }
            ]}}}
        }

        mock_execute.return_value = data
        result = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(result), 2)
        for r in result:
            self.assertTrue(r["volume"])
            self.assertTrue(r["missingKeys"])
        self.assertEqual(result[0]["missingKeys"], ["tag2"])
        missing_keys = set(result[1]["missingKeys"])
        self.assertEqual(missing_keys, {"tag1", "tag2"})

    def test_identical_tags(self, mock_execute):
        data = {"aws": {"ec2": {"volume": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "volumeId": "volumeId",
                "tags": [
                    {"key": "name", "value": "value"},
                    {"key": "tag1", "value": "1"}
                ],
                "state": "stopped",
                "instance": {
                    "tags": [
                        {"key": "tag2", "value": "2"},
                        {"key": "tag1", "value": "1"}
                    ]
                }
            }
            ]}}}
        }

        mock_execute.return_value = data
        result = app.lambda_handler(self.event, None)
        self.assertFalse(result)
        mock_execute.assert_called_once()

    def test_stopped_volumes(self, mock_execute):
        data = {"aws": {"ec2": {"volume": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "volumeId": "volumeId",
                "tags": [{"key": "name", "value": "value"}],
                "state": "stopped",
                "instance": {
                    "tags": [
                        {"key": "tag2", "value": "2"},
                        {"key": "tag1", "value": "1"}
                    ]
                }
            }
            ]}}}
        }

        mock_execute.return_value = data
        result = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
