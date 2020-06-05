import json
from graphqlclient import GraphQLClient
from termcolor import colored


class DiffObj:
    """
    Diff object to pass for making comparisons
    """
    def __init__(self, name, key, obj):
        self.name = name
        self.key = key
        self.obj = obj

    @classmethod
    def from_metadata(cls, name, key, obj):
        return cls(name, key, obj)


def diff_lists_of_scalars(list1, list2):
    """
    Compare lists list1 and list2 and returns a delta in color coded format

    :param list list1: list of elements
    :param list list2: list of elementss

    :return: the difference in human readable color coded format
    :rtype: list
    """
    list1 = frozenset(list1)
    list2 = frozenset(list2)

    missing = list1.difference(list2)
    diffs = [colored("- " + str(x), "red") for x in missing]
    added = list2.difference(list1)
    added = [colored("+ " + str(x), "green") for x in added]
    diffs.extend(added)

    return diffs


def format_string(obj, pad):
    """
    Takes an object and formats it into a json string

    :param object obj: object to format
    :param str pad: string to prefix the object with

    :return: formatted json string
    :rtype: str
    """
    s = json.dumps(obj, indent='\t', sort_keys=True)
    return pad + s.replace("\n", f"\n{pad}")


def diff_lists_of_objects(named_list1, named_list2, keys, prefix, depth):
    """
    Compares two of dicts to find the delta

    :param DiffObj named_list1:
    :param DiffObj named_list2:
    :param keys:
    :param prefix:
    :param depth:
    :return:
    """

    key = keys[prefix]
    list1 = sorted(named_list1.obj, key=lambda x: x[key])
    list2 = sorted(named_list2.obj, key=lambda x: x[key])

    pad = '\t' * depth

    pointer1 = 0
    pointer2 = 0
    diffs = []
    is_different = False
    while pointer1 < len(list1) and pointer2 < len(list2):
        item1 = list1[pointer1]
        item2 = list2[pointer2]

        if item1[key] < item2[key]:
            diffs.append(colored("- " + format_string(item1, pad), "red"))
            is_different = True
            pointer1 += 1
        elif item1[key] > item2[key]:
            diffs.append(colored("+ " + format_string(item2, pad), "green"))
            is_different = True
            pointer2 += 1
        else:
            item1 = DiffObj.from_metadata(named_list1.name, named_list1.key, item1)
            item2 = DiffObj.from_metadata(named_list2.name, named_list2.key, item2)
            object_diffs = diff_objects(item1, item2, keys, prefix, depth + 1)
            is_different = is_different or len(object_diffs) > 0
            diffs.extend(object_diffs)
            pointer1 += 1
            pointer2 += 1

    if is_different:
        diffs.insert(0, f'{pad[:-2]}"{prefix[prefix.rfind(".") + 1:]}": [')
        diffs.append(f'{pad[:-2]}]')

    return diffs


def diff_lists(obj1, obj2, keys, prefix="", depth=0):
    """
    Compares two lists of objects and returns the delta

    :param DiffObj obj1: list of objects
    :param DiffObj obj2: list of objects
    :param dict keys: key to compare on
    :param str prefix: key prefix
    :param int depth:

    :return: the delta in the objects
    :rtype: list
    """

    def prepend_prefix(string):
        s = string[len(pad):]
        return f'{pad[:-1]}"{prefix[prefix.rfind(".") + 1:]}": {s}'

    pad = '\t' * depth

    if not obj1.obj and not obj2.obj:
        return []
    elif not obj1.obj and obj2.obj:
        return [colored("+ " + prepend_prefix(format_string(obj2.obj, pad)), "green")]
    elif obj1.obj and not obj2.obj:
        return [colored("- " + prepend_prefix(format_string(obj1.obj, pad)), "red")]
    else:
        if isinstance(obj1.obj[0], dict):
            return diff_lists_of_objects(obj1, obj2, keys, prefix, depth + 1)
        else:
            return diff_lists_of_scalars(obj1.obj, obj2.obj)


def diff_objects(diff_obj1, diff_obj2, keys, prefix, depth):
    """
    Find the delta between two dict objects

    :param DiffObj diff_obj1: objects 1 to compare as base
    :param DiffObj diff_obj2: object 2 to compare with
    :param keys: keys to compare in the json
    :param prefix: key prefix when getting object properties
    :param depth: level in the object

    :return: the delta of the objects
    :rtype list
    """

    obj1 = diff_obj1.obj
    obj2 = diff_obj2.obj

    if diff_obj1.key in obj1:
        del obj1[diff_obj1.key]
        del obj2[diff_obj1.key]

    keys1 = sorted(obj1.keys())
    keys2 = sorted(obj2.keys())

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
            named_sub_list1 = DiffObj.from_metadata(diff_obj1.name, diff_obj1.key, item1)
            named_sub_list2 = DiffObj.from_metadata(diff_obj2.name, diff_obj2.key, item2)
            if isinstance(item1, dict):
                dict_diffs = diff_objects(named_sub_list1, named_sub_list2, keys, f"{prefix}.{key1}", depth + 1)
                is_different = is_different or len(dict_diffs) > 0
                diffs.extend(dict_diffs)
            elif isinstance(item1, list):
                list_diffs = diff_lists(named_sub_list1, named_sub_list2, keys, f"{prefix}.{key1}", depth + 1)
                is_different = is_different or len(list_diffs) > 0
                diffs.extend(list_diffs)
            elif isinstance(item1, str):
                if item1.replace(diff_obj1.name, "") != item2.replace(diff_obj2.name, ""):
                    diffs.append(colored(f'- {pad}"{key1}": "{item1}"', "red"))
                    diffs.append(colored(f'+ {pad}"{key2}": "{item2}"', "green"))
                    is_different = True
            index1 += 1
            index2 += 1

    if is_different:
        if prefix in keys:
            object_key = keys[prefix]
            diffs.insert(0, f'{pad}"{object_key}": "{obj1[object_key]}"')
            diffs.insert(0, pad[:-1] + "{")
        else:
            diffs.insert(0, f'{pad[:-1]}"{prefix[1:]}": ' + "{")
        diffs.append(pad[:-1] + "}")
    return diffs


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

    ref_account_id = event["params"]["ref_account_id"]
    new_account_id = event["params"]["new_account_id"]

    response = client.execute(query)
    response_json = json.loads(response)

    data = next(iter(response_json['data'].values()))['data']

    key = "farosAccountId"
    list1 = [x for x in data if x[key] == ref_account_id]
    list2 = [x for x in data if x[key] == new_account_id]
    obj_list1 = DiffObj.from_metadata(ref_account_id, key, list1)
    obj_list2 = DiffObj.from_metadata(new_account_id, key, list2)

    return "\n".join(diff_lists(obj_list1, obj_list2, keys))
