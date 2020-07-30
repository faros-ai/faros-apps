import app
import unittest

from faros.client import FarosClient
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class IAMRoleMissingPolicyTest(unittest.TestCase):
    def setUp(self):
        self.required_policy = "AmazonEC2FullAccess,AmazonECSFullAccess"
        self.event = {
            "farosToken": "token",
            "params": {
                "required_policy_arns": self.required_policy
            }
        }

    def test_role_no_policies(self, mock_execute):
        data = {"aws": {"iam": {"roleDetail": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "roleId": "roleId",
                "roleName": "AWSServiceRoleForTrustedAdvisor",
                "attachedManagedPolicies": []
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(results), 1)
        missing = frozenset(results[0]["missingPolicies"])
        required = {"AmazonEC2FullAccess", "AmazonECSFullAccess"}
        self.assertSetEqual(missing, required)

    def test_role_has_different_policy(self, mock_execute):
        data = {"aws": {"iam": {"roleDetail": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "roleId": "roleId",
                "roleName": "AWSServiceRoleForTrustedAdvisor",
                "attachedManagedPolicies": [
                    {"policyArn": "arn:aws:iam::xx:policy/service-role/"}
                ]
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(results), 1)
        missing = frozenset(results[0]["missingPolicies"])
        required = {"AmazonEC2FullAccess", "AmazonECSFullAccess"}
        self.assertSetEqual(missing, required)

    def test_some_policy(self, mock_execute):
        data = {"aws": {"iam": {"roleDetail": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "roleId": "roleId",
                "roleName": "AWSServiceRoleForTrustedAdvisor",
                "attachedManagedPolicies": [
                    {"policyArn": "AmazonECSFullAccess"}
                ]
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(results), 1)
        missing = frozenset(results[0]["missingPolicies"])
        self.assertSetEqual(missing, {"AmazonEC2FullAccess"})

    def test_role_has_all_policies(self, mock_execute):
        data = {"aws": {"iam": {"roleDetail": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "roleId": "roleId",
                "roleName": "AWSServiceRoleForTrustedAdvisor",
                "attachedManagedPolicies": [
                    {"policyArn": "AmazonECSFullAccess"},
                    {"policyArn": "AmazonEC2FullAccess"}
                ]
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
