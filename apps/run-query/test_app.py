import app
import unittest

from faros.client import FarosClient
from unittest.mock import patch


@patch('app.requests.get')
@patch.object(FarosClient, "graphql_execute")
class RunQueryTest(unittest.TestCase):
    def setUp(self):
        self.event = {
            "farosToken": "farosToken",
            "params": {"key": "query_name"}
        }

    def test_execute_saved_query(self, mock_execute, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "query": {"doc": "graphql_query"}
        }
        mock_execute.return_value = {"result": "1"}
        result = app.lambda_handler(self.event, None)
        mock_get.assert_called_once()
        mock_execute.assert_called_once()
        self.assertTrue(result)
        self.assertEqual(result, {"result": "1"})

    def test_execute_saved_query_with_data_path(self, mock_execute, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "query": {
                "doc": "graphql_query",
                "dataPath": "$.result[*].name"
            }
        }
        mock_execute.return_value = {"result": [
            {"name": "1"},
            {"name": "3"}
        ]}
        result = app.lambda_handler(self.event, None)
        mock_get.assert_called_once()
        mock_execute.assert_called_once()
        self.assertTrue(result)
        self.assertEqual(result, ["1", "3"])

    def test_query_not_found_throw_exception(self, mock_execute, mock_get):
        mock_get.return_value.status_code = 404
        with self.assertRaises(RuntimeError) as ex:
            app.lambda_handler(self.event, None)
        self.assertEqual(str(ex.exception), "no such query: 'query_name'")
        mock_get.assert_called_once()
        self.assertFalse(mock_execute.called)

    def test_no_key_throws_runtime(self, mock_execute, mock_get):
        bad_event = {"farosToken": "token", "params": {}}
        with self.assertRaises(RuntimeError) as ex:
            app.lambda_handler(bad_event, None)
        self.assertEqual(str(ex.exception), "missing 'key' parameter")
        self.assertFalse(mock_get.called)
        self.assertFalse(mock_execute.called)


if __name__ == "__main__":
    unittest.main()
