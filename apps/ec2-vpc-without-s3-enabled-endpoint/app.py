import json
from graphqlclient import GraphQLClient


def vpc_has_s3_enabled_endpoint(vpc):
    for vpc_endpoint in vpc["vpcEndpoints"]["data"]:
        if vpc_endpoint["state"] == "available" and vpc_endpoint["serviceName"].endswith(".s3"):
            return True
    return False


def lambda_handler(event, context):
    client = GraphQLClient("https://api.faros.ai/v0/graphql")
    client.inject_token("Bearer {}".format(event["farosToken"]))

    query = '''{
              ec2_vpc {
                data {
                  farosAccountId
                  farosRegionId                
                  vpcId
                  vpcEndpoints {
                    data {
                      state
                      serviceName
                    }
                  }
                }
              }
            }'''

    response = client.execute(query)
    response_json = json.loads(response)
    vpcs = response_json["data"]["ec2_vpc"]["data"]

    non_compliant_vpcs = [
        {"farosAccountId": vpc["farosAccountId"], "farosRegionId": vpc["farosRegionId"], "vpcId": vpc["vpcId"]}
        for vpc in vpcs if not vpc_has_s3_enabled_endpoint(vpc)
    ]

    return non_compliant_vpcs
