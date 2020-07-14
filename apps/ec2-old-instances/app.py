from datetime import datetime
from faros.client import FarosClient


def days_diff(date_string):
    return (datetime.utcnow() - datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")).days


def lambda_handler(event, context):
    client = FarosClient.from_event(event)

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
    cutoff = int(event["params"]["num_days"])
    return [
        i for i in instances
        if i["state"]["name"] == "running" and days_diff(i["launchTime"]) > cutoff
    ]
