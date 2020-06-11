import json
from graphqlclient import GraphQLClient


def is_bucket_public(bucket):
    if bucket["policyStatus"]:
        if bucket["policyStatus"]["isPublic"]:
            return True
    if bucket["publicAccessBlock"]:
        for k in bucket["publicAccessBlock"]:
            if not bucket["publicAccessBlock"][k]:
                return True
    return False


def lambda_handler(event, context):
    client = GraphQLClient("https://api.faros.ai/v0/graphql")
    client.inject_token("Bearer {}".format(event["farosToken"]))

    query = '''{
              s3_bucket {
                data {
                  farosAccountId
                  farosRegionId
                  name
                  policyStatus {
                    isPublic
                  }
                  publicAccessBlock {
                    blockPublicPolicy
                    restrictPublicBuckets
                    ignorePublicAcls
                    blockPublicAcls
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
        for b in buckets if is_bucket_public(b)
    ]
