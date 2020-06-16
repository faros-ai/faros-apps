from faros.client import FarosClient
from datetime import datetime


def days_diff(date_string):
    return (datetime.utcnow() - datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")).days


def has_old_access_keys(access_keys, max_days):
    return [key for key in access_keys if key["status"] == "Active" and days_diff(key["createDate"]) > max_days]


def lambda_handler(event, context):
    client = FarosClient.from_event(event)

    query = '''{
              aws {
                iam {
                  userDetail {
                    data {
                      farosAccountId
                      farosRegionId
                      userId
                      userName
                      accessKeys {
                        data {
                          status
                          createDate
                          accessKeyId
                        }
                      }
                    }
                  }
                }
              }
            }'''

    response = client.graphql_query(query)
    users = response["aws"]["iam"]["userDetail"]["data"]
    old_access_keys = []
    cutoff = int(event["params"]["max_days"])
    for user in users:
        old_keys = [key for key in user["accessKeys"]["data"]
                    if key["status"] == "Active" and days_diff(key["createDate"]) > cutoff]
        if old_keys:
            old_access_keys.append({
                "userId": user["userId"],
                "userName": user["userName"],
                "accessKeys": old_keys,
                "farosAccountId": user["farosAccountId"],
                "farosRegionId": user["farosRegionId"]
            })

    return old_access_keys
