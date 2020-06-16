from faros.client import FarosClient


def check_statement(policies):
    for policy in policies:
        if policy["Principal"] == "*":
            return True

    return False


def lambda_handler(event, context):
    client = FarosClient.from_event(event)

    query = '''{
              aws {
                ec2 {
                  vpcEndpoint {
                    data {
                      farosAccountId
                      farosRegionId
                      vpcId
                      policyDocument
                    }
                  }
                }
              }
            }'''

    response = client.graphql_query(query)
    endpoints = response["aws"]["ec2"]["vpcEndpoint"]["data"]
    return [
      e for e in endpoints
      if check_statement(e["policyDocument"]["Statement"])
    ]
