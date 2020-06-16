from faros.client import FarosClient


def missing_tags(instance_tags, volume_tags):
    return list(instance_tags - volume_tags)


def lambda_handler(event, context):
    client = FarosClient.from_event(event)

    query = '''{
              aws {
                ec2 {
                  volume {
                    data {
                      farosAccountId
                      farosRegionId
                      volumeId
                      tags {
                        key
                        value
                      }
                      state
                      instance {
                        tags {
                          key
                          value
                        }
                      }
                    }
                  }
                }
              }
            }'''

    response = client.graphql_query(query)
    volumes = response["aws"]["ec2"]["volume"]["data"]
    volumes_with_missing_tags = []
    for v in volumes:
        if v["state"] == "in-use":
            instance_tags = frozenset([t["key"] for t in v["instance"]["tags"]])
            volume_tags = frozenset([t["key"] for t in v["tags"]])
            delta = missing_tags(instance_tags, volume_tags)
            if delta:
                volumes_with_missing_tags.append({"volume": v, "missingKeys": delta})

    return volumes_with_missing_tags
