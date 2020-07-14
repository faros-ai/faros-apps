from faros.client import FarosClient


def check_policies(policies):
    bad_policies = frozenset(["AmazonEC2FullAccess", "AutoScalingFullAccess",
                              "ElasticLoadBalancingFullAccess", "AutoScalingConsoleFullAccess"])

    for policy in policies:
        if policy["policyName"] in bad_policies:
            return True

    return False


def lambda_handler(event, context):
    client = FarosClient.from_event(event)

    query = '''{
              aws {
                iam {
                  roleDetail {
                    data {
                      farosAccountId
                      farosRegionId
                      roleId
                      roleName
                      rolePolicyList {
                        policyName
                      }
                    }
                  }
                }
              }
            }'''

    response = client.graphql_execute(query)
    policies = response["aws"]["iam"]["roleDetail"]["data"]
    return [p for p in policies if check_policies(p["rolePolicyList"])]
