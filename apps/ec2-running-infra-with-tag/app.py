# Lists VMs and EBS volumes (in running state) by tag
from faros.client import FarosClient


def lambda_handler(event, context):
    client = FarosClient.from_event(event)
    tag_name = event["params"]["tag_name"]
    tag_value = event["params"]["tag_value"]

    query = '''{
              aws {
                ec2 {
                  instance {
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
                          size
                          volumeType
                        }
                      }
                    }
                  }
                }
              }
            }'''

    response = client.graphql_execute(query)

    instances = response["aws"]["ec2"]["instance"]["data"]
    infra = []
    for i in instances:
        if i["state"]["name"] == "running":
            for t in i["tags"]:
                if t["key"] == tag_name and t["value"] == tag_value:
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
