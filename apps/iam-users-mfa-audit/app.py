from faros.client import FarosClient


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
                      mfaDevices {
                        data {
                          serialNumber
                        }
                      }
                    }
                  }
                }
              }
            }'''

    response = client.graphql_execute(query)
    users = response["aws"]["iam"]["userDetail"]["data"]
    return [
        {
            "name": u["userName"],
            "id": u["userId"],
            "farosAccountId": u["farosAccountId"],
            "farosRegionId": u["farosRegionId"]
        }
        for u in users if not u["mfaDevices"]["data"]
    ]
