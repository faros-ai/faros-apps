import app
import unittest

from datetime import datetime, timedelta
from faros.client import FarosClient
from faros.utils import DATE_FORMAT
from unittest.mock import patch, Mock


# TODO: Add more tests for edge cases
@patch.object(FarosClient, "graphql_execute")
class CycleTimeTest(unittest.TestCase):
    def setUp(self):
        reference_time = 1609286400
        self.event = {"farosToken": "farosToken",
                      "params": {"reference_time_secs": reference_time, "window_days": 7, "compare_to_days": 7}}
        self.date = datetime.fromtimestamp(reference_time)

    def test_cycle_time(self, mock_execute):
        deploy1_time = (self.date - timedelta(days=1)).timestamp() * 1000
        deploy2_time = (self.date - timedelta(days=2)).timestamp() * 1000
        deploy3_time = (self.date - timedelta(days=8)).timestamp() * 1000
        deploy4_time = (self.date - timedelta(days=10)).timestamp() * 1000
        deploy5_time = (self.date - timedelta(days=3)).timestamp() * 1000
        deploy6_time = (self.date - timedelta(days=5)).timestamp() * 1000

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
                            "status": "Success",
                            "application": {
                                "name": "poseidon"
                            }
                        },
                        {
                            "endedAt": deploy3_time,
                            "startedAt": deploy3_time,
                            "status": "Success",
                            "application": {
                                "name": "poseidon"
                            }
                        },
                        {
                            "endedAt": deploy4_time,
                            "startedAt": deploy4_time,
                            "status": "Success",
                            "application": {
                                "name": "poseidon"
                            }
                        },
                        {
                            "endedAt": deploy5_time,
                            "startedAt": deploy5_time,
                            "status": "Success",
                            "application": {
                                "name": "phocus"
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
                    ]
                }
            }
        }
        mock_execute.return_value = query_data
        results = app.lambda_handler(self.event, None)
        self.assertEqual(
            results, {"Mean Cycle Time": 129600000, "Mean Cycle Time Change": -0.25})


if __name__ == "__main__":
    unittest.main()
