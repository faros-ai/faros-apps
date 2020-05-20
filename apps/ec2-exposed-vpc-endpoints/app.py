import json
from graphqlclient import GraphQLClient


def check_statement(policies):
    for policy in policies:
        if policy["Principal"] == "*":
            return True

    return False


def lambda_handler(event, context):
    client = GraphQLClient("https://api.faros.ai/v0/graphql")
    client.inject_token("Bearer {}".format(event["farosToken"]))

    query = '''{
              ec2_vpcEndpoint {
                data {
                  vpcId
                  policyDocument
                  farosAccountId
                  farosRegionId
                }
              }
            }'''

    response = client.execute(query)
    response_json = json.loads(response)
    endpoints = response_json["data"]["ec2_vpcEndpoint"]["data"]
    return [
      e for e in endpoints
      if check_statement(e["policyDocument"]["Statement"])
    ]
