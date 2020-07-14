import json
from faros.client import FarosClient
from urllib.parse import unquote


def has_full_star_policy(user):
    user_full_star_policies = [p for p in user["userPolicyList"] if full_star_policy(p)]
    group_full_star_policies = [p for g in user["groups"]["data"] for p in g["groupPolicyList"] if full_star_policy(p)]
    user_full_star_policies.extend(group_full_star_policies)
    return user_full_star_policies


def full_star_doc(doc):
    statements = doc["Statement"]

    statement_list = []
    if isinstance(statements, dict):
        statement_list = [statements]
    elif isinstance(statements, list):
        statement_list = statements
    else:
        return False

    for statement in statement_list:
        if statement["Effect"] == "Deny":
            continue

        if "Action" not in statement:
            continue

        if isinstance(statement["Action"], list):
            for action in statement["Action"]:
                if action == "*":
                    return True
        else:
            if statement["Action"] == "*":
                return True

    return False


def full_star_policy(policy):
    doc = policy["policyDocument"]
    decoded_doc = json.loads(unquote(doc))
    return full_star_doc(decoded_doc)


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
                      userPolicyList {
                        policyName
                        policyDocument
                      }
                      groups {
                        data {
                          groupId
                          groupName
                          attachedManagedPolicies {
                            policyArn
                            policyName
                          }
                          groupPolicyList {
                            policyName
                            policyDocument
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
    return [u for u in users if has_full_star_policy(u)]
