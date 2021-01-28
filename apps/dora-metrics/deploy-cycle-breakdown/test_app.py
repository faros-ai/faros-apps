import app
import unittest

from datetime import datetime, timedelta
from faros.client import FarosClient
from faros.utils import DATE_FORMAT
from unittest.mock import patch, Mock


# TODO: Add more tests for edge cases
@patch.object(FarosClient, "graphql_execute")
class DeployBreakdownTest(unittest.TestCase):
    def setUp(self):
        self.event = {"farosToken": "farosToken", "params": {}}

    def test_deploy_breakdown(self, mock_execute):
        query_data = {
            "cicd": {
                "deployments": {
                    "nodes": [
                        {
                            "id": "HmNpY2RfRGVwbG95bWVudC4WZC0wUjdEV0VMVzcUQ29kZURlcGxveQ==",
                            "status": "Success",
                            "startedAt": "1606787730000",
                            "endedAt": "1606788264404",
                            "application": {"name": "Poseidon"},
                            "build": {
                                "startedAt": "1606786425133",
                                "endedAt": "1606787284404",
                                "commitAssociations": {
                                    "nodes": [
                                        {
                                            "commit": {
                                                "createdAt": "1606786407000",
                                                "mergedPullRequest": {
                                                    "createdAt": "1606785593000",
                                                    "mergedAt": "1606786408000",
                                                    "reviews": {
                                                        "nodes": [
                                                            {
                                                                "state": "commented",
                                                                "submittedAt": "1606785606000"
                                                            },
                                                            {
                                                                "state": "approved",
                                                                "submittedAt": "1606785696000"
                                                            }
                                                        ]
                                                    }
                                                },
                                            }
                                        }
                                    ]
                                },
                            },
                        },
                        {
                            "id": "HmNpY2RfRGVwbG95bWVudC4WZC0xMkNZWUVQUzcUQ29kZURlcGxveQ==",
                            "status": "Success",
                            "startedAt": "1606273465777",
                            "endedAt": "1606273959013",
                            "application": {"name": "Poseidon"},
                            "build": {
                                "startedAt": "1606272273172",
                                "endedAt": "1606273047068",
                                "commitAssociations": {
                                    "nodes": [
                                        {
                                            "commit": {
                                                "createdAt": "1606272253000",
                                                "mergedPullRequest": {
                                                    "createdAt": "1606147445000",
                                                    "mergedAt": "1606272254000",
                                                    "reviews": {
                                                        "nodes": []
                                                    }
                                                }
                                            }
                                        }
                                    ]
                                },
                            },
                        },
                        {
                            "id": "HmNpY2RfRGVwbG95bWVudC4WZC00M1pCRTNSSjgUQ29kZURlcGxveQ==",
                            "status": "Success",
                            "startedAt": "1609827660734",
                            "endedAt": "1609828154785",
                            "application": {"name": "Poseidon"},
                            "build": {
                                "startedAt": "1609826607256",
                                "endedAt": "1609827293660",
                                "commitAssociations": {
                                    "nodes": [
                                        {
                                            "commit": {
                                                "createdAt": "1609826592000",
                                                "mergedPullRequest": {
                                                    "createdAt": "1609781318000",
                                                    "mergedAt": "1609826593000",
                                                    "reviews": {
                                                        "nodes": [
                                                            {
                                                                "state": "approved",
                                                                "submittedAt": "1609781418000"
                                                            },
                                                            {
                                                                "state": "approved",
                                                                "submittedAt": "1609781518000"
                                                            },
                                                        ]
                                                    }
                                                }
                                            }
                                        },
                                        {
                                            "commit": {
                                                "createdAt": "1609826002000",
                                                "mergedPullRequest": {
                                                    "createdAt": "1609781318000",
                                                    "mergedAt": "1609826003000",
                                                    "reviews": {
                                                        "nodes": [
                                                            {
                                                                "state": "approved",
                                                                "submittedAt": "1609781418000"
                                                            },
                                                            {
                                                                "state": "approved",
                                                                "submittedAt": "1609781518000"
                                                            },
                                                        ]
                                                    }
                                                }
                                            }
                                        }

                                    ]
                                },
                            },
                        },
                        {
                            "id": "HmNpY2RfRGVwbG95bWVudC4WZC00REk1T05WUjcUQ29kZURlcGxveQ==",
                            "status": "Success",
                            "startedAt": "1606166762198",
                            "endedAt": "1606167277214",
                            "application": {"name": "Poseidon"},
                            "build": {
                                "startedAt": "1606165701440",
                                "endedAt": "1606166380795",
                                "commitAssociations": {
                                    "nodes": [
                                        {
                                            "commit": {
                                                "createdAt": "1606165671000",
                                                "mergedPullRequest": None
                                            }
                                        }
                                    ]
                                },
                            },
                        },
                    ]
                }
            }
        }

        mock_execute.return_value = query_data
        results = app.lambda_handler(self.event, None)
        self.assertEqual(
            results,
            [
                {
                    "id": "HmNpY2RfRGVwbG95bWVudC4WZC00REk1T05WUjcUQ29kZURlcGxveQ==",
                    "application": "Poseidon",
                    "ended_at": 1606167277214,
                    "pr_review_time": None,
                    "pr_merge_time": None,
                    "build_time": 679355,
                    "deploy_time": 515016,
                },
                {
                    "id": "HmNpY2RfRGVwbG95bWVudC4WZC0xMkNZWUVQUzcUQ29kZURlcGxveQ==",
                    "application": "Poseidon",
                    "ended_at": 1606273959013,
                    "pr_review_time": None,
                    "pr_merge_time": 124809000,
                    "build_time": 773896,
                    "deploy_time": 493236,
                },
                {
                    "id": "HmNpY2RfRGVwbG95bWVudC4WZC0wUjdEV0VMVzcUQ29kZURlcGxveQ==",
                    "application": "Poseidon",
                    "ended_at": 1606788264404,
                    "pr_review_time": 103000,
                    "pr_merge_time": 712000,
                    "build_time": 859271,
                    "deploy_time": 534404,
                },
                {
                    "id": "HmNpY2RfRGVwbG95bWVudC4WZC00M1pCRTNSSjgUQ29kZURlcGxveQ==",
                    "application": "Poseidon",
                    "ended_at": 1609828154785,
                    "pr_review_time": 100000,
                    "pr_merge_time": 45175000,
                    "build_time": 686404,
                    "deploy_time": 494051,
                },
            ],
        )


if __name__ == "__main__":
    unittest.main()
