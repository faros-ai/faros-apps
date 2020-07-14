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
                      }
                      attachments {
                        instanceId
                      }
                    }
                  }
                }
              }
            }'''

    response = client.graphql_execute(query)
    volumes = response["aws"]["ec2"]["volume"]["data"]
    return [v for v in volumes if not v["attachments"]]
