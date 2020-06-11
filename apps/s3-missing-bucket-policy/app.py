import json
from graphqlclient import GraphQLClient


def has_missing_policy(policy, required_policy_statements):
    if not required_policy_statements:
        missing = ["No policies defined"] if not policy else []
        return missing
    if not policy:
        return required_policy_statements
    else:
        doc = json.loads(policy["policy"])
        attached = [stmt["Sid"] for stmt in doc["Statement"]]
        missing = list(frozenset(required_policy_statements).difference(attached))
        return missing


def lambda_handler(event, context):
    client = GraphQLClient("https://api.faros.ai/v0/graphql")
    client.inject_token("Bearer {}".format(event["farosToken"]))

    query = '''{
              s3_bucket {
                data {
                  farosAccountId
                  farosRegionId
                  name
                  policy {
                    policy
                  }
                }
              }
            }'''

    response = client.execute(query)
    response_json = json.loads(response)
    buckets = response_json["data"]["s3_bucket"]["data"]

    required_policy_param = event.get("params").get("required_policy_statement")
    required_policy_statements = required_policy_param.split(",") if required_policy_param else None

    buckets_missing_policy = []
    for bucket in buckets:
        missing = has_missing_policy(bucket["policy"], required_policy_statements)
        if missing:
            buckets_missing_policy.append(
                {
                    "name": bucket["name"],
                    "missingPolicy": missing,
                    "farosAccountId": bucket["farosAccountId"],
                    "farosRegionId": bucket["farosRegionId"],

                })

    return buckets_missing_policy
