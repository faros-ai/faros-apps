from faros.client import FarosClient


def check_subnets(subnets, count):
    return [s for s in subnets if s["availableIpAddressCount"] < count]


def lambda_handler(event, context):
    client = FarosClient.from_event(event)
    count = int(event["params"]["ip_count"])
    if count < 1:
        raise ValueError("IP count should be a positive integer")

    query = '''{
              aws {
                ec2 {
                  subnet {
                    data {
                      farosAccountId
                      farosRegionId
                      subnetId
                      availableIpAddressCount
                    }
                  }
                }
              }
            }'''

    response = client.graphql_execute(query)
    subnets = response["aws"]["ec2"]["subnet"]["data"]
    return [
      subnet for subnet in subnets
      if subnet["availableIpAddressCount"] < count
    ]
