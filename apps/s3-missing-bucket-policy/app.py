from faros.client import FarosClient


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
    client = FarosClient.from_event(event)

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

    response = client.graphql_query(query)
    buckets = response["aws"]["s3"]["bucket"]["data"]

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
