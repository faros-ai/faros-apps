from faros.client import FarosClient


def lambda_handler(event, context):
    client = FarosClient.from_event(event)

    query = '''{
              aws {
                ec2 {
                  securityGroup {
                    data {
                      farosAccountId
                      farosRegionId
                      groupId
                      instances {
                        data {
                          instanceId
                        }
                      }
                    }
                  }
                }
              }
            }'''

    response = client.graphql_query(query)
    groups = response["aws"]["ec2"]["securityGroup"]["data"]
    return [g for g in groups if not g["instances"]["data"]]
