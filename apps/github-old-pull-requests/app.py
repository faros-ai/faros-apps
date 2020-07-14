from faros.client import FarosClient
from faros.utils import time_diff


def lambda_handler(event, context):
    client = FarosClient.from_event(event)

    query = '''{
              github {
                pullRequest {
                  data {
                    number
                    title
                    state
                    repo_name
                    locked
                    created_at
                    user_login
                    assignee_login
                  }
                }
              }
            }'''

    response = client.graphql_execute(query)
    pull_requests = response["github"]["pullRequest"]["data"]
    cutoff = int(event["params"]["max_days"])

    return [
        p for p in pull_requests
        if time_diff(p["created_at"]).days > cutoff and p["state"] == "open"
    ]