from faros.client import FarosClient
import json


def check_statements(policy_doc):
    policy = json.loads(policy_doc)
    for elem in policy.get('Statement', []):
        if elem["Principal"] == "*":
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

    response = client.graphql_execute(query)
    endpoints = response["aws"]["ec2"]["vpcEndpoint"]["data"]
    return [
      e for e in endpoints
      if check_statements(e["policyDocument"])
    ]
