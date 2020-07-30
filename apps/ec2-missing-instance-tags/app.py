from faros.client import FarosClient


def missing_tags(required, existing):
    return list(required - existing)


def lambda_handler(event, context):
    client = FarosClient.from_event(event)
    required_keys = frozenset(event["params"]["keys"].split(","))

    query = '''{
              aws {
                ec2 {
                  instance {
                    data {
                      farosAccountId
                      farosRegionId
                      instanceId
                      tags {
                        key
                        value
                      }
                    }
                  }
                }
              }
            }'''

    response = client.graphql_execute(query)
    instances = response["aws"]["ec2"]["instance"]["data"]
    tagless_instances = [{"instance": i, "missingKeys": missing_tags(
        required_keys, frozenset([t["key"] for t in i["tags"]]))} for i in instances]
    tagless_instances = [i for i in tagless_instances if i["missingKeys"]]

    return tagless_instances
