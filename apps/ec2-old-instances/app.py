from faros.client import FarosClient
from faros.utils import time_diff


def lambda_handler(event, context):
    client = FarosClient.from_event(event)
    cutoff = int(event["params"]["num_days"])
    if cutoff < 1:
        raise ValueError("num days should be a positive integer")

    query = '''{
              aws {
                ec2 {
                  instance {
                    data {
                      farosAccountId
                      farosRegionId
                      instanceId
                      launchTime
                      state {
                        name
                      }
                    }
                  }
                }
              }
            }'''

    response = client.graphql_execute(query)
    instances = response["aws"]["ec2"]["instance"]["data"]
    return [
        i for i in instances
        if i["state"]["name"] == "running"
        and time_diff(i["launchTime"]).days > cutoff
    ]
