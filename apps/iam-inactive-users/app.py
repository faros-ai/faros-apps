from faros.client import FarosClient
from datetime import datetime


def days_diff(date_string):
    return (datetime.utcnow() - datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")).days


def lambda_handler(event, context):
    client = FarosClient.from_event(event)

    query = '''{
              aws {
                iam {
                  user {
                    data {
                      farosAccountId
                      farosRegionId
                      userId
                      userName
                      passwordLastUsed
                    }
                  }
                }
              }
            }'''

    response = client.graphql_query(query)
    users = response["aws"]["iam"]["user"]["data"]
    cutoff = int(event["params"]["max_days"])
    return [
        u for u in users
        if u["passwordLastUsed"] is None or days_diff(u["passwordLastUsed"]) > cutoff
    ]
