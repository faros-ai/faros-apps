import app
import unittest

from faros.client import FarosClient
from faros.utils import DATE_FORMAT
from datetime import datetime, timedelta
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class EC2OldInstances(unittest.TestCase):
    def setUp(self):
        self.event = {
            "farosToken": "farosToken",
            "params": {"num_days": 2}
        }
        self.now = datetime.utcnow()

    def test_get_old_instances(self, mocked_execute):
        new_instance = (self.now - timedelta(hours=5)).strftime(DATE_FORMAT)
        old_instance = (self.now - timedelta(days=3)).strftime(DATE_FORMAT)
        old_instance2 = (self.now - timedelta(days=10)).strftime(DATE_FORMAT)
        data = {"aws": {"ec2": {"instance": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "instanceId": "instanceId4",
                "launchTime": old_instance,
                "state": {"name": "running"}
            },
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "instanceId": "instanceId2",
                "launchTime": old_instance2,
                "state": {"name": "running"}
            },
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "instanceId": "instanceId3",
                "launchTime": new_instance,
                "state": {"name": "running"}
            }
            ]}}}
        }

        mocked_execute.return_value = data
        result = app.lambda_handler(self.event, None)
        mocked_execute.assert_called_once()
        self.assertEqual(len(result), 2)
        old = {i["instanceId"] for i in result}
        self.assertSetEqual(old, {"instanceId2", "instanceId4"})

    def test_missing_cutoff(self, mocked_execute):
        mocked_execute.return_value = None
        with self.assertRaises(KeyError):
            app.lambda_handler({"farosToken": "token"}, None)
        self.assertFalse(mocked_execute.called)

    def test_invalid_cutoff_value(self, mocked_execute):
        event = {
            "farosToken": "token",
            "params": {"num_days": "day"}
        }
        mocked_execute.return_value = None
        with self.assertRaises(ValueError):
            app.lambda_handler(event, None)
        self.assertFalse(mocked_execute.called)

        event = {
            "farosToken": "token",
            "params": {"num_days": "-2"}
        }
        with self.assertRaises(ValueError):
            app.lambda_handler(event, None)
        self.assertFalse(mocked_execute.called)


if __name__ == "__main__":
    unittest.main()
