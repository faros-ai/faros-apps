from faros.client import FarosClient


def get_policy_arns(user):
    policy_arns = [p["policyArn"] for p in user["attachedManagedPolicies"]]
    group_policy_arns = [p["policyArn"] for g in user["groups"]["data"] for p in g["attachedManagedPolicies"]]
    policy_arns.extend(group_policy_arns)
    return policy_arns


def get_missing_policies(required, attached):
    return list(frozenset(required).difference(attached))


def lambda_handler(event, context):
    client = FarosClient.from_event(event)

    query = """{
              aws {
                iam {
                  userDetail {
                    data {
                      farosAccountId
                      farosRegionId
                      userId
                      userName
                      attachedManagedPolicies {
                        policyArn
                        policyName
                      }
                      groups {
                        data {
                          groupId
                          groupName
                          attachedManagedPolicies {
                            policyArn
                            policyName
                          }
                        }
                      }
                    }
                  }
                }
              }
            }"""

    response = client.graphql_execute(query)
    users = response["aws"]["iam"]["userDetail"]["data"]
    users_without_policies = []
    required_policy_arns = event["params"]["required_policy_arns"].split(",")

    for user in users:
        policies = get_policy_arns(user)
        missing_policies = get_missing_policies(required_policy_arns, policies)
        if missing_policies:
            users_without_policies.append({
                "userId": user["userId"],
                "userName": user["userName"],
                "farosAccountId": user["farosAccountId"],
                "farosRegionId": user["farosRegionId"],
                "missing_policies": missing_policies}
            )

    return users_without_policies
