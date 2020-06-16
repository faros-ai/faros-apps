import json
from faros.client import FarosClient


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
                      publicIpAddress
                    }
                  }
                }
              }
            }'''

    response = client.graphql_query(query)
    instances = response["aws"]["ec2"]["instance"]["data"]
    return [i for i in instances if i["publicIpAddress"] is not None]
