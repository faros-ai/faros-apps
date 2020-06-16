from faros.client import FarosClient


def get_missing_policies(required, attached):
    return list(frozenset(required).difference(attached))


def lambda_handler(event, context):
    client = FarosClient.from_event(event)

    query = """{
              aws {
                iam {
                  roleDetail {
                    data {
                      farosAccountId
                      farosRegionId
                      roleId
                      roleName
                      attachedManagedPolicies {
                        policyArn
                        policyName
                      }
                    }
                  }
                }
              }
            }"""

    response = client.graphql_query(query)
    roles = response["aws"]["iam"]["roleDetail"]["data"]
    required_policy_arns = event["params"]["required_policy_arns"].split(",")
    roles_without_policies = []
    for role in roles:
        policies = [p["policyArn"] for p in role["attachedManagedPolicies"]]
        missing_policies = get_missing_policies(required_policy_arns, policies)
        if missing_policies:
            roles_without_policies.append({
                "roleId": role["roleId"],
                "roleName": role["roleName"],
                "farosAccountId": role["farosAccountId"],
                "farosRegionId": role["farosRegionId"],
                "missing_policies": missing_policies
            })

    return roles_without_policies
