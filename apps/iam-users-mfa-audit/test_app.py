import app
import unittest

from faros.client import FarosClient
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class IAMUserMFAAuditTest(unittest.TestCase):
    def setUp(self):
        self.event = {"farosToken": "farosToken"}

    def test_user_no_mfa(self, mock_execute):
        data = {"aws": {"iam": {"userDetail": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "userId": "HephaestusId",
                "userName": "Hephaestus",
                "mfaDevices": {"data": []}
            },
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "userId": "HephaestusId2",
                "userName": "Hephaestus2",
                "mfaDevices": {"data": []}
            },
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "userId": "dolos",
                "userName": "dolos",
                "mfaDevices": {"data": [{"serialNumber": "828238"}]}
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(results), 2)
        users = {u["userId"] for u in results}
        self.assertSetEqual(users, {"HephaestusId", "HephaestusId2"})


if __name__ == "__main__":
    unittest.main()
