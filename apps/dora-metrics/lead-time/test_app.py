import app
import unittest

from datetime import datetime, timedelta
from faros.client import FarosClient
from unittest.mock import patch


# TODO: Add more tests for multiple apps and edge cases
@patch.object(FarosClient, "graphql_execute")
class LeadTimeTest(unittest.TestCase):
    def setUp(self):
        reference_time = 1609286400
        self.event = {"farosToken": "farosToken",
                      "params": {"reference_time_secs": reference_time, "window_days": 7, "compare_to_days": 7}}
        self.date = datetime.fromtimestamp(reference_time)

    def test_lead_time(self, mock_execute):
        deploy1_time = (self.date - timedelta(days=0.5)).timestamp() * 1000
        create1_time = (self.date - timedelta(days=1)).timestamp() * 1000
        deploy2_time = (self.date - timedelta(days=1.5)).timestamp() * 1000
        create2_time = (self.date - timedelta(days=2)).timestamp() * 1000
        deploy3_time = (self.date - timedelta(days=2.5)).timestamp() * 1000
        create3_time = (self.date - timedelta(days=3)).timestamp() * 1000
        deploy4_time = (self.date - timedelta(days=8)).timestamp() * 1000
        create4_time = (self.date - timedelta(days=9)).timestamp() * 1000
        deploy5_time = (self.date - timedelta(days=10)).timestamp() * 1000
        create5_time = (self.date - timedelta(days=11)).timestamp() * 1000
        deploy6_time = (self.date - timedelta(days=3)).timestamp() * 1000
        create6_time = (self.date - timedelta(days=4)).timestamp() * 1000

        query_data = {
            "vcs": {
                "commits": {
                    "nodes": [
                        {
                            "createdAt": create1_time,
                            "buildAssociations": {
                                "nodes": [
                                    {
                                        "build": {
                                            "deployments": {
                                                "nodes": [
                                                    {
                                                        "endedAt": deploy1_time,
                                                        "status": "Success",
                                                        "application": {
                                                            "name": "Poseidon"
                                                        }
                                                    }
                                                ]
                                            }
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "createdAt": create2_time,
                            "buildAssociations": {
                                "nodes": [
                                    {
                                        "build": {
                                            "deployments": {
                                                "nodes": [
                                                    {
                                                        "endedAt": deploy2_time,
                                                        "status": "Success",
                                                        "application": {
                                                            "name": "Poseidon"
                                                        }
                                                    }
                                                ]
                                            }
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "createdAt": create3_time,
                            "buildAssociations": {
                                "nodes": [
                                    {
                                        "build": {
                                            "deployments": {
                                                "nodes": [
                                                    {
                                                        "endedAt": deploy3_time,
                                                        "status": "Success",
                                                        "application": {
                                                            "name": "Poseidon"
                                                        }
                                                    }
                                                ]
                                            }
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "createdAt": create4_time,
                            "buildAssociations": {
                                "nodes": [
                                    {
                                        "build": {
                                            "deployments": {
                                                "nodes": [
                                                    {
                                                        "endedAt": deploy4_time,
                                                        "status": "Success",
                                                        "application": {
                                                            "name": "Poseidon"
                                                        }
                                                    }
                                                ]
                                            }
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "createdAt": create5_time,
                            "buildAssociations": {
                                "nodes": [
                                    {
                                        "build": {
                                            "deployments": {
                                                "nodes": [
                                                    {
                                                        "endedAt": deploy5_time,
                                                        "status": "Success",
                                                        "application": {
                                                            "name": "Poseidon"
                                                        }
                                                    }
                                                ]
                                            }
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "createdAt": create6_time,
                            "buildAssociations": {
                                "nodes": [
                                    {
                                        "build": {
                                            "deployments": {
                                                "nodes": [
                                                    {
                                                        "endedAt": deploy6_time,
                                                        "status": "Success",
                                                        "application": {
                                                            "name": "phocus"
                                                        }
                                                    }
                                                ]
                                            }
                                        }
                                    }
                                ]
                            }
                        }

                    ]
                }
            }
        }
        mock_execute.return_value = query_data
        results = app.lambda_handler(self.event, None)
        self.assertEqual(results, {"Mean Lead Time": 54000000,
                                   "Mean Lead Time Change": -0.375})

    def test_empty_data(self, mock_execute):
        query_data = {
            "vcs": {
                "commits": {
                    "nodes": [
                        {
                            "createdAt": "1611801851000",
                            "buildAssociations": {
                                "nodes": []
                            }
                        },
                        {
                            "createdAt": "1608595310000",
                            "buildAssociations": {
                                "nodes": []
                            }
                        }
                    ]
                }
            }
        }
        mock_execute.return_value = query_data
        results = app.lambda_handler(self.event, None)
        self.assertEqual(
            results, {"Mean Lead Time": None, "Mean Lead Time Change": None})


if __name__ == "__main__":
    unittest.main()
