import app
import unittest

from faros.client import FarosClient
from unittest.mock import patch
from urllib.parse import quote


@patch.object(FarosClient, "graphql_execute")
class IAMGroupsWithFullStarPolicy(unittest.TestCase):
    def setUp(self):
        self.event = {"farosToken": "token"}

    def test_group_no_policies(self, mock_execute):
        data = {"aws": {"iam": {"groupDetail": {"data": [
            {
                "groupId": "groupId1",
                "groupName": "testUserGroup",
                "groupPolicyList": []
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertFalse(results)

    def test_group_deny_policy(self, mock_execute):
        policy = ('{"Statement":[{"Effect":"Deny",'
                  '"Action":"*","Resource":"*"}]}')
        data = {"aws": {"iam": {"groupDetail": {"data": [
            {
                "groupId": "groupId1",
                "groupName": "testUserGroup",
                "groupPolicyList": [
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
        data = {"aws": {"iam": {"groupDetail": {"data": [
            {
                "groupId": "groupId1",
                "groupName": "testUserGroup",
                "groupPolicyList": [
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

    def test_group_policy_no_action(self, mock_execute):
        policy = '{"Statement":[{"Effect":"Allow","Resource":"*"}]}'
        data = {"aws": {"iam": {"groupDetail": {"data": [
            {
                "groupId": "groupId1",
                "groupName": "testUserGroup",
                "groupPolicyList": [
                    {
                        "policyName": "PowerUserAccess",
                        "policyDocument": policy
                    }
                ]
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertFalse(results)

    def test_group_policy_full_star(self, mock_execute):
        policy = ('{"Statement":[{"Effect":"Allow","Resource":"*"},'
                  '{"Effect":"Allow","Action":"*","Resource":"*"}]}')
        data = {"aws": {"iam": {"groupDetail": {"data": [
            {
                "groupId": "testUserGroupId1",
                "groupName": "testUserGroup",
                "groupPolicyList": [
                    {
                        "policyName": "PowerUserAccess",
                        "policyDocument": policy
                    }
                ]
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["groupId"], "testUserGroupId1")


if __name__ == "__main__":
    unittest.main()
