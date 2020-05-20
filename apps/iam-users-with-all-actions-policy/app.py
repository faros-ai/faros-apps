import json
from graphqlclient import GraphQLClient
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


def full_star_policy(policyList):
    for policy in policyList:
        for doc in policy["policyDocument"]:
            decoded_doc = json.loads(unquote(doc))
            if full_star_doc(decoded_doc):
                return True

    return False


def lambda_handler(event, context):
    client = GraphQLClient("https://api.faros.ai/v0/graphql")
    client.inject_token("Bearer {}".format(event["farosToken"]))

    query = """{
              iam_userDetail {
                data {
                  userId
                  userName
                  attachedManagedPolicies {
                    policyName
                    policyArn
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
                        policyName
                        policyArn
                      }
                      groupPolicyList {
                        policyName
                        policyDocument
                      }
                    }
                  }
                  farosAccountId
                  farosRegionId
                }
              }
            }"""

    response = client.execute(query)
    response_json = json.loads(response)
    users = response_json["data"]["iam_userDetail"]["data"]
    return [u for u in users if has_full_star_policy(u)]
