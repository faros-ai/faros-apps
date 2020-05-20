import json
from graphqlclient import GraphQLClient


def missing_tags(required, existing):
    return list(required - existing)


def lambda_handler(event, context):
    client = GraphQLClient("https://api.faros.ai/v0/graphql")
    client.inject_token("Bearer {}".format(event["farosToken"]))

    query = '''{
              ec2_instance {
                data {
                  instanceId
                  tags {
                    key
                  }
                  farosAccountId
                  farosRegionId
                }
              }
            }'''

    response = client.execute(query)
    response_json = json.loads(response)
    instances = response_json["data"]["ec2_instance"]["data"]
    required_keys = frozenset(event["params"]["keys"].split(","))
    tagless_instances = [{"instance": i, "missingKeys": missing_tags(
        required_keys, frozenset([t["key"] for t in i["tags"]]))} for i in instances]
    tagless_instances = [i for i in tagless_instances if i["missingKeys"]]

    return tagless_instances
