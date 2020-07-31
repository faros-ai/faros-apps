import json
from faros.client import FarosClient


def get_missing_policies(policy, required_policies):
    if not policy:
        return required_policies
    else:
        doc = json.loads(policy["policy"])
        attached = [stmt["Sid"] for stmt in doc["Statement"]]
        missing = list(frozenset(required_policies).difference(attached))
        return missing


def lambda_handler(event, context):
    client = FarosClient.from_event(event)
    required_policy_param = event["params"].get("required_policy_statement")
    if not required_policy_param:
        raise KeyError("Required policy statements not supplied. You can "
                       "define them with -p "
                       "required_policy_statement=<comma-separated-policies>")

    required_policies = required_policy_param.split(",")

    query = '''{
              aws {
                s3 {
                  bucket {
                    data {
                      farosAccountId
                      farosRegionId
                      name
                      policy {
                        policy
                      }
                    }
                  }
                }
              }
            }'''

    response = client.graphql_execute(query)
    buckets = response["aws"]["s3"]["bucket"]["data"]

    buckets_missing_policy = []
    for bucket in buckets:
        missing = get_missing_policies(bucket["policy"], required_policies)
        if missing:
            buckets_missing_policy.append(
                {
                    "name": bucket["name"],
                    "missingPolicies": missing,
                    "farosAccountId": bucket["farosAccountId"],
                    "farosRegionId": bucket["farosRegionId"],

                })

    return buckets_missing_policy
