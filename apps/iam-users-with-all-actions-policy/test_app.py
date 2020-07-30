import app
import unittest

from faros.client import FarosClient
from unittest.mock import patch
from urllib.parse import quote


@patch.object(FarosClient, "graphql_execute")
class IAMUsersWithAllActionsTest(unittest.TestCase):
    def setUp(self):
        self.event = {"farosToken": "token"}

    def test_user_no_policies(self, mock_execute):
        data = {"aws": {"iam": {"userDetail": {"data": [
            {
                "userId": "HephaestusId",
                "userPolicyList": [],
                "groups": {"data": []}
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertFalse(results)

    def test_user_deny_policy(self, mock_execute):
        policy = quote('{"Statement":[{"Effect":"Deny",'
                       '"Action":"*","Resource":"*"}]}')
        data = {"aws": {"iam": {"userDetail": {"data": [
            {
                "userId": "HephaestusId",
                "userPolicyList": [
                    {
                        "policyName": "AssumeRole",
                        "policyDocument": policy
                    }
                ],
                "groups": {"data": [{"groupPolicyList": [
                    {
                        "policyName": "AssumeRole",
                        "policyDocument": policy
                    }
                ]}]}
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertFalse(results)

    def test_user_policy_full_star(self, mock_execute):
        policy = quote('{"Statement":[{"Effect":"Allow",'
                       '"Action":"*","Resource":"*"}]}')
        data = {"aws": {"iam": {"userDetail": {"data": [
            {
                "userId": "HephaestusId",
                "userPolicyList": [
                    {
                        "policyName": "AssumeRole",
                        "policyDocument": policy
                    }
                ],
                "groups": {"data": []}
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["userId"], "HephaestusId")

    def test_user_full_star_on_group(self, mock_execute):
        policy = quote('{"Statement":[{"Effect":"Allow",'
                       '"Action":"*","Resource":"*"}]}')
        data = {"aws": {"iam": {"userDetail": {"data": [
            {
                "userId": "HephaestusId",
                "userPolicyList": [],
                "groups": {"data": [{"groupPolicyList": [
                    {
                        "policyName": "AssumeRole",
                        "policyDocument": policy
                    }
                ]}]}
            }
        ]}}}}
        mock_execute.return_value = data
        results = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["userId"], "HephaestusId")


if __name__ == "__main__":
    unittest.main()
