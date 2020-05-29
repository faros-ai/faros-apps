# Lists VMs and EBS volumes (in running state) by tag
import json
from graphqlclient import GraphQLClient


def lambda_handler(event, context):
    client = GraphQLClient("https://api.faros.ai/v0/graphql")
    client.inject_token("Bearer " + event["farosToken"])

    query = '''{
            ec2_instance {
              data {
                farosAccountId
                farosRegionId
                instanceId
                instanceType
                state {
                  name
                }
                tags {
                  key
                  value
                }
                volumes {
                  data {
                    volumeType
                    size
                  }
                }
              }
            }
    }'''

    response = client.execute(query)
    response_json = json.loads(response)

    instances = response_json["data"]["ec2_instance"]["data"]
    infra = []
    for i in instances:
        if i["state"]["name"] == "running":
            for t in i["tags"]:
                if t["key"] == event["params"]["tag_name"] and t["value"] == event["params"]["tag_value"]:
                    infra.append(
                        {
                            "account": i["farosAccountId"],
                            "region": i["farosRegionId"],
                            "instanceId": i["instanceId"],
                            "instanceType": i["instanceType"],
                            "volumes": i["volumes"]["data"]
                        }
                    )
    return infra
