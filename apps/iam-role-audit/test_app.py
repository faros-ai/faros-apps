import app
import unittest

from faros.client import FarosClient
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class IAMRoleAuditTest(unittest.TestCase):
    def setUp(self):
        self.event = {"farosToken": "farosToken"}

    def test_no_policy_list(self, mock_execute):
        data = {"aws": {"iam": {"roleDetail": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "roleId": "roleId",
                "roleName": "AWSServiceRoleForTrustedAdvisor",
                "rolePolicyList": []
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertFalse(results)

    def test_has_policy_allowed(self, mock_execute):
        data = {"aws": {"iam": {"roleDetail": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "roleId": "roleId",
                "roleName": "AWSServiceRoleForTrustedAdvisor",
                "rolePolicyList": [{"policyName": "iamPassRoleForSagemaker"}]
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertFalse(results)

    def test_has_forbidden_policy(self, mock_execute):
        data = {"aws": {"iam": {"roleDetail": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "roleId": "roleIdWithForbidden",
                "roleName": "AWSServiceRoleForTrustedAdvisor",
                "rolePolicyList": [{"policyName": "AmazonEC2FullAccess"}]
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["roleId"], "roleIdWithForbidden")


if __name__ == "__main__":
    unittest.main()
