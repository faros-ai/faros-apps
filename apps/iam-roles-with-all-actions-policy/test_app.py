import app
import unittest

from faros.client import FarosClient
from unittest.mock import patch
from urllib.parse import quote


@patch.object(FarosClient, "graphql_execute")
class IAMRolesWithAllActionsTest(unittest.TestCase):
    def setUp(self):
        self.event = {"farosToken": "token"}

    def test_role_no_policies(self, mock_execute):
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

    def test_role_deny_policy(self, mock_execute):
        policy = ('{"Statement":[{"Effect":"Deny",'
                  '"Action":"*","Resource":"*"}]}')
        data = {"aws": {"iam": {"roleDetail": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "roleId": "roleId",
                "roleName": "AWSServiceRoleForTrustedAdvisor",
                "rolePolicyList": [
                    {
                        "policyName": "AdministratorAccess",
                        "policyDocument": policy
                    }
                ]
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertFalse(results)

    def test_role_policy_allow_not_full_star(self, mock_execute):
        policy = quote('{"Statement":[{"Effect":"Allow",'
                       '"Action":"iamPassRole","Resource":"*"}]}')
        data = {"aws": {"iam": {"roleDetail": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "roleId": "roleId",
                "roleName": "AWSServiceRoleForTrustedAdvisor",
                "rolePolicyList": [
                    {
                        "policyName": "AdministratorAccess",
                        "policyDocument": policy
                    }
                ]
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertFalse(results)

    def test_role_policy_no_action(self, mock_execute):
        policy = '{"Statement":[{"Effect":"Allow","Resource":"*"}]}'
        data = {"aws": {"iam": {"roleDetail": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "roleId": "roleId",
                "roleName": "AWSServiceRoleForTrustedAdvisor",
                "rolePolicyList": [
                    {
                        "policyName": "AdministratorAccess",
                        "policyDocument": policy
                    }
                ]
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertFalse(results)

    def test_role_policy_full_star(self, mock_execute):
        policy = ('{"Statement":[{"Effect":"Allow",'
                  '"Action":"*","Resource":"*"}]}')
        data = {"aws": {"iam": {"roleDetail": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "roleId": "roleFullStar",
                "roleName": "AWSServiceRoleForTrustedAdvisor",
                "rolePolicyList": [
                    {
                        "policyName": "AdministratorAccess",
                        "policyDocument": policy
                    }
                ]
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["roleId"], "roleFullStar")

    def test_role_policy_full_star_quoted(self, mock_execute):
        policy = quote('{"Statement":[{"Effect":"Allow",'
                       '"Action":"*","Resource":"*"}]}')
        data = {"aws": {"iam": {"roleDetail": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "roleId": "roleFullStar",
                "roleName": "AWSServiceRoleForTrustedAdvisor",
                "rolePolicyList": [
                    {
                        "policyName": "AdministratorAccess",
                        "policyDocument": policy
                    }
                ]
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["roleId"], "roleFullStar")


if __name__ == "__main__":
    unittest.main()
