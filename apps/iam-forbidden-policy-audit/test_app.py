import app
import unittest

from faros.client import FarosClient
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class IAMForbiddenPolicyTest(unittest.TestCase):
    def setUp(self):
        self.event = {
            "farosToken": "token",
            "params": {
                "forbidden_policy_arn":
                    "arn:aws:iam::aws:policy/AmazonEC2FullAccess"
            }
        }

    def test_user_no_policy(self, mock_execute):
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
        result = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertFalse(result)

    def test_different_policy_attached(self, mock_execute):
        data = {"aws": {"iam": {"userDetail": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "userId": "HephaestusId",
                "userName": "Hephaestus",
                "attachedManagedPolicies": [
                    {
                        "policyArn": "arn:aws:iam::aws:policy/ECS_FullAccess",
                        "policyName": "ECS_FullAccess"
                    }
                ],
                "groups": {"data": [
                    {
                        "groupId": "groupId",
                        "groupName": "S3Admins",
                        "attachedManagedPolicies": [
                            {
                                "policyArn": '''policy/S3FullAccess''',
                                "policyName": "AmazonS3FullAccess"
                            }
                        ]
                    }
                ]}
            }
        ]}}}}
        mock_execute.return_value = data
        result = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertFalse(result)

    def test_policy_user_attached(self, mock_execute):
        policyArn = "arn:aws:iam::aws:policy/AmazonEC2FullAccess"
        data = {"aws": {"iam": {"userDetail": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "userId": "HephaestusId",
                "userName": "Hephaestus",
                "attachedManagedPolicies": [
                    {
                        "policyArn": policyArn,
                        "policyName": "AmazonEC2FullAccess"
                    }
                ],
                "groups": {"data": []}
            }
        ]}}}}
        mock_execute.return_value = data
        result = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["userId"], "HephaestusId")
        self.assertTrue(result[0]["sources"]["onUser"])
        self.assertFalse(result[0]["sources"]["inGroups"])

    def test_policy_in_groups(self, mock_execute):
        policyArn = "arn:aws:iam::aws:policy/AmazonEC2FullAccess"
        data = {"aws": {"iam": {"userDetail": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "userId": "HephaestusId",
                "userName": "Hephaestus",
                "attachedManagedPolicies": [],
                "groups": {"data": [
                    {
                        "groupName": "S3Admins",
                        "attachedManagedPolicies": [
                            {
                                "policyArn": policyArn,
                            }
                        ]
                    },
                    {
                        "groupName": "S3SuperAdmins",
                        "attachedManagedPolicies": [
                            {
                                "policyArn": policyArn,
                            }
                        ]
                    }
                ]}
            }
        ]}}}}
        mock_execute.return_value = data
        result = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["userId"], "HephaestusId")
        self.assertEqual(len(result[0]["sources"]["inGroups"]), 2)
        in_groups = set(result[0]["sources"]["inGroups"])
        self.assertSetEqual(in_groups, {"S3SuperAdmins", "S3Admins"})
        self.assertFalse(result[0]["sources"]["onUser"])

    def test_policy_on_user_and_group(self, mock_execute):
        policyArn = "arn:aws:iam::aws:policy/AmazonEC2FullAccess"
        data = {"aws": {"iam": {"userDetail": {"data": [
            {
                "farosAccountId": "accountId",
                "farosRegionId": "farosId",
                "userId": "HephaestusId",
                "userName": "Hephaestus",
                "attachedManagedPolicies": [
                    {
                        "policyArn": policyArn,
                        "policyName": "AmazonEC2FullAccess"
                    }
                ],
                "groups": {"data": [
                    {
                        "groupName": "S3Admins",
                        "attachedManagedPolicies": [
                            {
                                "policyArn": policyArn,
                            }
                        ]
                    }
                ]}
            }
        ]}}}}
        mock_execute.return_value = data
        result = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["userId"], "HephaestusId")
        self.assertEqual(len(result[0]["sources"]["inGroups"]), 1)
        in_groups = set(result[0]["sources"]["inGroups"])
        self.assertSetEqual(in_groups, {"S3Admins"})
        self.assertTrue(result[0]["sources"]["onUser"])

    def test_no_policy_param(self, mock_execute):
        event = {"farosToken": "farosToken", "params": {"other": "aksk"}}
        with self.assertRaises(KeyError):
            app.lambda_handler(event, None)
        self.assertFalse(mock_execute.called)


if __name__ == "__main__":
    unittest.main()
