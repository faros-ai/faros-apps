import app
import unittest

from faros.client import FarosClient
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class IAMUserMissingPolicyTest(unittest.TestCase):
    def setUp(self):
        self.required_policy = "AmazonEC2FullAccess,AmazonECSFullAccess"
        self.policy_set = {"AmazonEC2FullAccess", "AmazonECSFullAccess"}
        self.event = {
            "farosToken": "token",
            "params": {
                "required_policy_arns": self.required_policy
            }
        }

    def test_user_no_policies(self, mock_execute):
        data = {"aws": {"iam": {"userDetail": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "userId": "HephaestusId",
                "userName": "Hephaestus",
                "attachedManagedPolicies": [],
                "groups": {"data": []}
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(results), 1)
        missing = frozenset(results[0]["missingPolicies"])
        self.assertSetEqual(missing, self.policy_set)

    def test_user_has_different_policy(self, mock_execute):
        data = {"aws": {"iam": {"userDetail": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "userId": "HephaestusId",
                "userName": "Hephaestus",
                "attachedManagedPolicies": [
                    {"policyArn": "arn:aws:iam::xx:policy/service-role/"}
                ],
                "groups": {"data": []}
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(results), 1)
        missing = frozenset(results[0]["missingPolicies"])
        self.assertSetEqual(missing, self.policy_set)

    def test_some_policy_on_user(self, mock_execute):
        data = {"aws": {"iam": {"userDetail": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "userId": "HephaestusId",
                "userName": "Hephaestus",
                "attachedManagedPolicies": [
                    {"policyArn": "AmazonECSFullAccess"}
                ],
                "groups": {"data": []}
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(results), 1)
        missing = frozenset(results[0]["missingPolicies"])
        self.assertSetEqual(missing, {"AmazonEC2FullAccess"})

    def test_has_all_policies_on_user(self, mock_execute):
        data = {"aws": {"iam": {"userDetail": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "userId": "HephaestusId",
                "userName": "Hephaestus",
                "attachedManagedPolicies": [
                    {"policyArn": "AmazonECSFullAccess"},
                    {"policyArn": "AmazonEC2FullAccess"}
                ],
                "groups": {"data": []}
            }
        ]}}}}

        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertFalse(results)

    def test_has_all_policies_on_group(self, mock_execute):
        data = {"aws": {"iam": {"userDetail": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "userId": "HephaestusId",
                "userName": "Hephaestus",
                "attachedManagedPolicies": [],
                "groups": {"data": [
                    {
                        "attachedManagedPolicies": [
                            {"policyArn": "AmazonECSFullAccess"},
                            {"policyArn": "AmazonEC2FullAccess"}
                        ]
                    }
                ]}
            }
        ]}}}}

        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertFalse(results)

    def test_required_policies_not_defined(self, mock_execute):
        event = {"farosToken": "token"}
        mock_execute.return_value = None
        with self.assertRaises(KeyError):
            app.lambda_handler(event, None)
        self.assertFalse(mock_execute.called)


if __name__ == "__main__":
    unittest.main()
