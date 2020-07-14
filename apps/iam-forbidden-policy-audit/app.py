from faros.client import FarosClient


def check_for_policies(user, policy_arn):
    ret = {"compliant": True, "onUser": False, "inGroups": []}
    for p in user["attachedManagedPolicies"]:
        if p["policyArn"] == policy_arn:
            ret["onUser"] = True
            ret["compliant"] = False
            break
    for g in user["groups"]["data"]:
        for p in g["attachedManagedPolicies"]:
            if p["policyArn"] == policy_arn:
                ret["inGroups"].append(g["groupName"])
                ret["compliant"] = False

    return ret


def format_output(user, policies):
    del policies["compliant"]
    return {"userId": user["userId"], "userName": user["userName"], "accountId": user["farosAccountId"],
            "sources": policies}


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

    bad_policy_users = [(u, check_for_policies(u, event["params"]["forbidden_policy_arn"])) for u in users]
    return [format_output(u, p) for (u, p) in bad_policy_users if not p["compliant"]]
