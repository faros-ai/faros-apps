from faros.client import FarosClient
from faros.utils import DiffObj, diff_objects


def lambda_handler(event, context):
    client = FarosClient.from_event(event)

    query = '''{
              aws {
                iam {
                  userDetail {
                    data {
                      farosAccountId
                      userId
                      attachedManagedPolicies {
                        policyArn
                        policyName
                      }
                      groups {
                        data {
                          arn
                          groupId
                          groupName
                          attachedManagedPolicies {
                            policyArn
                            policyName
                          }
                          groupPolicyList {
                            policyName
                          }
                        }
                      }
                      permissionsBoundary {
                        permissionsBoundaryArn
                        permissionsBoundaryType
                      }
                      userPolicyList {
                        policyName
                      }
                    }
                  }
                }
              }
            }'''

    keys = {"": "userId",
            ".attachedManagedPolicies": "policyArn",
            ".groups.data": "groupName",
            ".groups.data.attachedManagedPolicies": "policyArn",
            ".groups.data.groupPolicyList": "policyName",
            ".mfaDevices.data": "serialNumber",
            ".permissionsBoundary": "permissionsBoundaryArn",
            ".tags": "key",
            ".userPolicyList": "policyName"}

    ref_user_id = event["params"]["ref_user_id"]
    new_user_id = event["params"]["new_user_id"]

    response = client.graphql_query(query)

    data = response["aws"]["iam"]["userDetail"]["data"]

    key = "userId"
    user1 = next(x for x in data if x[key] == ref_user_id)
    user2 = next(x for x in data if x[key] == new_user_id)
    obj1 = DiffObj(ref_user_id, key, user1)
    obj2 = DiffObj(new_user_id, key, user2)

    return diff_objects(obj1, obj2, keys).pretty_string()
