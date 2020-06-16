from faros.client import FarosClient


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
    client = FarosClient.from_event(event)

    query = '''{
              aws {
                s3 {
                  bucket {
                    data {
                      farosAccountId
                      farosRegionId
                      name
                      policyStatus {
                        isPublic
                      }
                      publicAccessBlock {
                        blockPublicAcls
                        blockPublicPolicy
                        ignorePublicAcls
                        restrictPublicBuckets
                      }
                    }
                  }
                }
              }
            }'''

    response = client.graphql_query(query)
    buckets = response["aws"]["s3"]["bucket"]["data"]

    return [
        {
            "farosAccountId": b["farosAccountId"],
            "farosRegionId": b["farosRegionId"],
            "name": b["name"]
        }
        for b in buckets if is_bucket_public(b)
    ]
