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
    volumes_with_stopped_instances = []
    for volume in volumes:
        if volume.get("instance"):
            if volume["instance"]["state"]["name"] == "stopped":
                volumes_with_stopped_instances.append(volume)

    return volumes_with_stopped_instances
