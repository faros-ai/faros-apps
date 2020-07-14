from faros.client import FarosClient


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
                }
              }
            }'''

    response = client.graphql_execute(query)
    buckets = response["aws"]["s3"]["bucket"]["data"]

    return [
        {
            "farosAccountId": b["farosAccountId"],
            "farosRegionId": b["farosRegionId"],
            "name": b["name"]
        }
        for b in buckets if not b["encryption"]
    ]
