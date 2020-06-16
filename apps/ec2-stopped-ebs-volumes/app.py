from faros.client import FarosClient


def lambda_handler(event, context):
    client = FarosClient.from_event(event)

    query = '''{
              aws {
                ec2 {
                  volume {
                    data {
                      farosAccountId
                      farosRegionId
                      volumeId
                      state
                      instance {
                        instanceId
                        state {
                          name
                        }
                      }
                    }
                  }
                }
              }
            }'''

    response = client.graphql_query(query)
    volumes = response["aws"]["ec2"]["volume"]["data"]
    return [i for i in volumes if i["instance"]["state"]["name"] == "stopped"]
