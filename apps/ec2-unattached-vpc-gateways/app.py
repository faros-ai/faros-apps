from faros.client import FarosClient


def lambda_handler(event, context):
    client = FarosClient.from_event(event)

    query = '''{
              aws {
                ec2 {
                  internetGateway {
                    data {
                      farosAccountId
                      farosRegionId
                      internetGatewayId
                      attachments {
                        vpcId
                      }
                    }
                  }
                }
              }
            }'''

    response = client.graphql_query(query)
    gateways = response["aws"]["ec2"]["internetGateway"]["data"]
    return [g for g in gateways if not g["attachments"]]
