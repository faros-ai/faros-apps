import app
import unittest

from datetime import datetime, timedelta
from faros.client import FarosClient
from faros.utils import DATE_FORMAT
from unittest.mock import patch


# TODO: Add more tests for edge cases
@patch.object(FarosClient, "graphql_execute")
class FailureRateTest(unittest.TestCase):
    def setUp(self):
        reference_time = 1609286400
        self.event = {"farosToken": "farosToken",
                      "params": {"reference_time_secs": reference_time, "window_days": 7, "compare_to_days": 7}}
        self.date = datetime.fromtimestamp(reference_time)

    def test_failure_rate(self, mock_execute):
        deploy1_time = (self.date - timedelta(days=1)).timestamp() * 1000
        deploy2_time = (self.date - timedelta(days=2)).timestamp() * 1000
        deploy3_time = (self.date - timedelta(days=3)).timestamp() * 1000
        deploy4_time = (self.date - timedelta(days=8)).timestamp() * 1000
        deploy5_time = (self.date - timedelta(days=10)).timestamp() * 1000
        deploy6_time = (self.date - timedelta(days=1)).timestamp() * 1000
        deploy7_time = (self.date - timedelta(days=2)).timestamp() * 1000
        deploy8_time = (self.date - timedelta(days=4)).timestamp() * 1000
        deploy9_time = (self.date - timedelta(days=6)).timestamp() * 1000

        query_data = {
            "cicd": {
                "deployments": {
                    "nodes": [
                        {
                            "endedAt": deploy1_time,
                            "startedAt": deploy1_time,
                            "status": "Success",
                            "application": {
                                "name": "poseidon"
                            }
                        },
                        {
                            "endedAt": deploy2_time,
                            "startedAt": deploy2_time,
                            "status": "Failed",
                            "application": {
                                "name": "poseidon"
                            }
                        },
                        {
                            "endedAt": deploy3_time,
                            "startedAt": deploy3_time,
                            "status": "Failed",
                            "application": {
                                "name": "poseidon"
                            }
                        },
                        {
                            "endedAt": deploy4_time,
                            "startedAt": deploy4_time,
                            "status": "Failed",
                            "application": {
                                "name": "poseidon"
                            }
                        },
                        {
                            "endedAt": deploy5_time,
                            "startedAt": deploy5_time,
                            "status": "Failed",
                            "application": {
                                "name": "poseidon"
                            }
                        },
                        {
                            "endedAt": deploy6_time,
                            "startedAt": deploy6_time,
                            "status": "Success",
                            "application": {
                                "name": "phocus"
                            }
                        },
                        {
                            "endedAt": deploy7_time,
                            "startedAt": deploy7_time,
                            "status": "Failed",
                            "application": {
                                "name": "phocus"
                            }
                        },
                        {
                            "endedAt": deploy8_time,
                            "startedAt": deploy8_time,
                            "status": "Failed",
                            "application": {
                                "name": "phocus"
                            }
                        },
                        {
                            "endedAt": deploy9_time,
                            "startedAt": deploy9_time,
                            "status": "Failed",
                            "application": {
                                "name": "phocus"
                            }
                        }
                    ]
                }
            }
        }
        mock_execute.return_value = query_data
        results = app.lambda_handler(self.event, None)
        self.assertAlmostEqual(results["Change Failure Rate"], 5/7)
        self.assertAlmostEqual(results["Change Failure Rate Change"], -2/7)
        self.assertEqual(results["Mean Time between Failures"], 144000000)
        self.assertAlmostEqual(
            results["Mean Time between Failures Change"], -1/6)


if __name__ == "__main__":
    unittest.main()
