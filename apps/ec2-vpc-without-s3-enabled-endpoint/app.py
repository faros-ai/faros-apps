from faros.client import FarosClient


def vpc_has_s3_enabled_endpoint(vpc):
    for vpc_endpoint in vpc["vpcEndpoints"]["data"]:
        if vpc_endpoint["state"] == "available" and vpc_endpoint["serviceName"].endswith(".s3"):
            return True
    return False


def lambda_handler(event, context):
    client = FarosClient.from_event(event)

    query = '''{
              aws {
                ec2 {
                  vpc {
                    data {
                      farosAccountId
                      farosRegionId
                      vpcId
                      vpcEndpoints {
                        data {
                          state
                          serviceName
                        }
                      }
                    }
                  }
                }
              }
            }'''

    response = client.graphql_query(query)
    vpcs = response["aws"]["ec2"]["vpc"]["data"]

    non_compliant_vpcs = [
        {"farosAccountId": vpc["farosAccountId"], "farosRegionId": vpc["farosRegionId"], "vpcId": vpc["vpcId"]}
        for vpc in vpcs if not vpc_has_s3_enabled_endpoint(vpc)
    ]

    return non_compliant_vpcs
