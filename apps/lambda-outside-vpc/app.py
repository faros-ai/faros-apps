import json
from graphqlclient import GraphQLClient


def get_all_functions(functions):
    all_functions = []
    for region in functions:
        all_functions.extend(region["functions"])

    return all_functions


def lambda_handler(event, context):
    client = GraphQLClient("https://api.faros.ai/v0/graphql")
    client.inject_token("Bearer {}".format(event["farosToken"]))

    query = '''{
              lambda_functionConfiguration {
                data {
                  functionArn
                  functionName
                  vpcConfig {
                    subnetIds
                  }
                  farosAccountId
                  farosRegionId                  
                }
              }
            }'''

    response = client.execute(query)
    response_json = json.loads(response)
    functions = response_json["data"]["lambda_functionConfiguration"]["data"]

    return [f for f in functions if not f["vpcConfig"] or not f["vpcConfig"]["subnetIds"]]
