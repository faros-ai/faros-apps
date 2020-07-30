import app
import unittest

from faros.client import FarosClient
from unittest.mock import patch


@patch.object(FarosClient, "graphql_execute")
class OutputEmailerTest(unittest.TestCase):
    def setUp(self):
        self.event = {
            "farosToken": "farosToken",
            "params": {"report_name": "TestReport", "recipient": "test@acme"},
            "data": [{"results": "1"}]
        }

    def test_send_email(self, mock_execute):
        mock_execute.return_value = "success"
        result = app.lambda_handler(self.event, None)
        mock_execute.assert_called_once()
        self.assertEqual(result, "success")


if __name__ == "__main__":
    unittest.main()
