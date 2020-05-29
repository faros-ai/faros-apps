import json
from graphqlclient import GraphQLClient
from termcolor import colored

def diff_lists_of_scalars(list1, list2):
    print(f"scalars: {list1}\t{list2}")
    list1 = frozenset(list1)
    list2 = frozenset(list2)

    missing = list(list1 - list2)
    diffs = [colored("- " + str(x), "red") for x in missing]
    added = list(list2 - list1)
    added = [colored("+ " + str(x), "green") for x in added]
    diffs.extend(added)

    return diffs

def format_string(string, pad):
    s = json.dumps(string, indent='\t', sort_keys=True)
    return pad + s.replace("\n", f"\n{pad}")

def diff_lists_of_objects(list1, list2, keys, prefix, depth):
    print(f"diff_lists_of_objects: {prefix}")    
    key = keys[prefix]
    list1 = sorted(list1, key = lambda x: x[key])
    list2 = sorted(list2, key = lambda x: x[key])

    pad = '\t' * depth

    pointer1 = 0
    pointer2 = 0
    diffs = []
    is_different = False
    while pointer1 < len(list1) and pointer2 < len(list2):
        item1 = list1[pointer1]
        item2 = list2[pointer2]

        print(f"comparing {item1[key]} to {item2[key]}")
        if item1[key] < item2[key]:
            diffs.append(colored("- " + format_string(item1, pad), "red"))
            is_different = True
            pointer1 += 1
        elif item1[key] > item2[key]:
            diffs.append(colored("+ " + format_string(item2, pad), "green"))
            is_different = True
            pointer2 += 1
        else:
            object_diffs = diff_objects(item1, item2, keys, prefix, depth + 1)
            is_different = is_different or len(object_diffs) > 0
            diffs.extend(object_diffs)
            pointer1 += 1
            pointer2 += 1

    if is_different:
        diffs.insert(0, f'{pad[:-2]}"{prefix[prefix.rfind(".") + 1:]}": [')
        diffs.append(f'{pad[:-2]}]')

    return diffs

def diff_lists(list1, list2, keys, prefix = "", depth = 0):
    def prepend_prefix(string):
        s = string[len(pad):]
        return f'{pad[:-1]}"{prefix[prefix.rfind(".") + 1:]}": {s}'

    print(f"diff_lists: {prefix}")
    pad = '\t' * depth

    if list1 == [] and list2 == []:
        return []
    elif list1 == [] and list2 != []:
        return [colored("+ " + prepend_prefix(format_string(list2, pad)), "green")]
    elif list1 != [] and list2 == []:
        return [colored("- " + prepend_prefix(format_string(list1, pad)), "red")]
    else:
        if isinstance(list1[0], dict):
            return diff_lists_of_objects(list1, list2, keys, prefix, depth + 1)
        else:
            return diff_lists_of_scalars(list1, list2)

    return []



def diff_objects(obj1, obj2, keys, prefix, depth):
    print(f"diff_objects: {prefix}")    
    if "farosAccountId" in obj1:
        del obj1["farosAccountId"]
        del obj2["farosAccountId"]
    keys1 = sorted(obj1.keys())
    keys2 = sorted(obj2.keys())
    print(f"keys: {keys1}\t{keys2}")

    pad = '\t' * depth
    index1 = 0
    index2 = 0
    diffs = []
    is_different = False
    while index1 < len(keys1) and index2 < len(keys2):
        key1 = keys1[index1]
        key2 = keys2[index2]
        item1 = obj1[key1]
        item2 = obj2[key2]
        
        if key1 < key2:
            diffs.append(colored(f'- {key1}: {item1}', "red"))
            index1 += 1
        elif key1 > key2:
            diffs.append(colored(f'+ {key2}: {item2}', "green"))
            index2 += 1
        else:            
            if isinstance(item1, dict):
                dict_diffs = diff_objects(item1, item2, keys, f"{prefix}.{key1}", depth + 1)
                is_different = is_different or len(dict_diffs) > 0
                diffs.extend(dict_diffs)
            elif isinstance(item1, list):
                list_diffs = diff_lists(item1, item2, keys, f"{prefix}.{key1}", depth + 1)
                is_different = is_different or len(list_diffs) > 0
                diffs.extend(list_diffs)
            elif isinstance(item1, str):
                global ref_account_id
                global new_account_id
                if item1.replace(ref_account_id, "") != item2.replace(new_account_id, ""):
                    diffs.append(colored(f'- {pad}"{key1}": "{item1}"', "red"))
                    diffs.append(colored(f'+ {pad}"{key2}": "{item2}"', "green"))
                    is_different = True
            index1 += 1
            index2 += 1

    print(f"finished {prefix}, diff = {is_different}")
    if is_different:
        object_name = ""
        if prefix != "":
            object_name = f"{prefix[1: ]}: "
        if prefix in keys:
            object_key = keys[prefix]
            diffs.insert(0, f'{pad}"{object_key}": "{obj1[object_key]}"')
            diffs.insert(0, pad[:-1] + "{")
        else:
            diffs.insert(0, f'{pad[:-1]}"{prefix[1:]}": ' + "{")            
        diffs.append(pad[:-1] + "}")
    return diffs

ref_account_id = ""
new_account_id = ""

def lambda_handler(event, context):
    client = GraphQLClient("https://api.faros.ai/v0/graphql")
    client.inject_token("Bearer " + event["farosToken"])

    query = '''{
              iam_userDetail {
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
                        policyDocument
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
                  tags {
                    key
                    value
                  }
                  userPolicyList {
                    policyName
                    policyDocument
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

    global ref_account_id
    global new_account_id
    ref_account_id = event["params"]["ref_account_id"]
    new_account_id = event["params"]["new_account_id"]

    response = client.execute(query)
    response_json = json.loads(response)

    object_name = next(iter(response_json["data"]))
    data = response_json["data"][object_name]["data"]

    list1 = [x for x in data if x["farosAccountId"] == ref_account_id]
    list2 = [x for x in data if x["farosAccountId"] == new_account_id]

    return "\n".join(diff_lists(list1, list2, keys))
