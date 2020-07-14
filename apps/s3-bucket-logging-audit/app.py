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
                      logging {
                        loggingEnabled {
                          targetBucket
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
            "name": b["name"],
            "farosAccountId": b["farosAccountId"],
            "farosRegionId": b["farosRegionId"]
        }
        for b in buckets if not b["logging"]["loggingEnabled"]
    ]
