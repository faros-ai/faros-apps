import json

from faros.client import FarosClient
from urllib.parse import unquote


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


def full_star_policy(policy_list):
    for policy in policy_list:
        doc = policy["policyDocument"]
        decoded_doc = json.loads(unquote(doc))
        if full_star_doc(decoded_doc):
            return True

    return False


def lambda_handler(event, context):
    client = FarosClient.from_event(event)

    query = """{
              aws {
                iam {
                  groupDetail {
                    data {
                      farosAccountId
                      farosRegionId
                      groupName
                      groupId
                      groupPolicyList {
                        policyDocument
                        policyName
                      }
                    }
                  }
                }
              }
            }"""

    response = client.graphql_execute(query)
    groups = response["aws"]["iam"]["groupDetail"]["data"]
    return [g for g in groups if full_star_policy(g["groupPolicyList"])]
