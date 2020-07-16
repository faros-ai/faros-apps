from faros.client import FarosClient
import jsonpath_rw_ext
import requests

# TODO: Read this URL from somewhere else.
QUERY_BASE_URL = 'https://api.faros.ai/v0/queries/'

def lambda_handler(event, context):
    client = FarosClient.from_event(event)

    # First, fetch the query from the input key.
    query_key = event["params"].get("key")
    res = requests.get(QUERY_BASE_URL + query_key)
    if res.status_code == 404: # Nicer error if the query did not exist.
      raise RuntimeError('no such query: ' + query_key)
    res.raise_for_status() # Any other error type.
    query = res.json()['query']

    # Then, execute it and apply any JSONPath expression.
    data = client.graphql_execute(query['doc'])
    json_path = query.get('dataPath')
    if json_path:
      data = jsonpath_rw_ext.match(json_path, data)
    return data
