import json
from faros.client import FarosClient
from faros.utils import DiffObj, diff_lists
from termcolor import colored

def lambda_handler(event, context):
    client = FarosClient.from_event(event)

    query = '''{
              aws {
                iam {
                  userDetail {
                    data {
                      farosAccountId
                      arn
                      userId
                      userName
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
                      mfaDevices {
                        data {
                          serialNumber
                        }
                      }
                      permissionsBoundary {
                        permissionsBoundaryArn
                        permissionsBoundaryType
                      }
                      userPolicyList {
                        policyName
                      }
                      tags {
                        key
                        value
                      }
                    }
                  }
                }
              }
            }'''

    keys = {"": "userName",
            ".attachedManagedPolicies": "policyArn",
            ".groups.data": "groupName",
            ".groups.data.attachedManagedPolicies": "policyArn",
            ".groups.data.groupPolicyList": "policyName",
            ".mfaDevices.data": "serialNumber",
            ".permissionsBoundary": "permissionsBoundaryArn",
            ".tags": "key",
            ".userPolicyList": "policyName"}

    ref_account_id = event["params"]["ref_account_id"]
    new_account_id = event["params"]["new_account_id"]

    response = client.graphql_execute(query)

    data = response["aws"]["iam"]["userDetail"]["data"]

    key = "farosAccountId"
    list1 = [x for x in data if x[key] == ref_account_id]
    list2 = [x for x in data if x[key] == new_account_id]
    obj_list1 = DiffObj(ref_account_id, key, list1)
    obj_list2 = DiffObj(new_account_id, key, list2)

    return diff_lists(obj_list1, obj_list2, keys).pretty_string()
