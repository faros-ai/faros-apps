import app
import unittest

from faros.client import FarosClient
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class Ec2UnencryptedEBSVolumesTest(unittest.TestCase):
    def test_get_unencrypted_volumes(self, mock_execute):
        event = {"farosToken": "token"}
        data = {"aws": {"ec2": {"volume": {"data": [
            {
                "farosAccountId": "farosAccountId",
                "farosRegionId": "farosRegionId",
                "volumeId": "vol-4",
                "encrypted": False
            },
            {
                "farosAccountId": "farosAccountId",
                "farosRegionId": "farosRegionId",
                "volumeId": "vol-1",
                "encrypted": False
            },
            {
                "farosAccountId": "farosAccountId",
                "farosRegionId": "farosRegionId",
                "volumeId": "vol-2",
                "encrypted": True
            }
        ]}}}}

        mock_execute.return_value = data
        results = app.lambda_handler(event, None)
        self.assertEqual(len(results), 2)
        unencrypted = {v["volumeId"] for v in results}
        self.assertSetEqual(unencrypted, {"vol-1", "vol-4"})
        mock_execute.assert_called_once()


if __name__ == "__main__":
    unittest.main()
