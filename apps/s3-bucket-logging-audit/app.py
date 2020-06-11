import json
from graphqlclient import GraphQLClient


def lambda_handler(event, context):
    client = GraphQLClient("https://api.faros.ai/v0/graphql")
    client.inject_token("Bearer {}".format(event["farosToken"]))

    query = '''{
              s3_bucket {
                after
                data {
                  farosAccountId
                  farosRegionId
                  name
                  logging {
                    loggingEnabled {
                      targetBucket
                    }
                  }
                }
              }
            }'''

    response = client.execute(query)
    response_json = json.loads(response)
    buckets = response_json["data"]["s3_bucket"]["data"]

    return [
        {
            "name": b["name"],
            "farosAccountId": b["farosAccountId"],
            "farosRegionId": b["farosRegionId"]
        }
        for b in buckets if not b["logging"]["loggingEnabled"]
    ]
