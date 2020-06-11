import json
from graphqlclient import GraphQLClient


def lambda_handler(event, context):
    client = GraphQLClient("https://api.faros.ai/v0/graphql")
    client.inject_token("Bearer {}".format(event["farosToken"]))

    query = '''{
              s3_bucket {
                data {
                  farosAccountId
                  farosRegionId
                  name
                  encryption {
                    rules {
                      applyServerSideEncryptionByDefault {
                        kmsMasterKeyID
                        sseAlgorithm
                      }
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
            "farosAccountId": b["farosAccountId"],
            "farosRegionId": b["farosRegionId"],
            "name": b["name"]
        }
        for b in buckets if not b["encryption"]
    ]
