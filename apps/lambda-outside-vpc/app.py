from faros.client import FarosClient


def get_all_functions(functions):
    all_functions = []
    for region in functions:
        all_functions.extend(region["functions"])

    return all_functions


def lambda_handler(event, context):
    client = FarosClient.from_event(event)

    query = '''{
              aws {
                lambda {
                  functionConfiguration {
                    data {
                      farosAccountId
                      farosRegionId
                      functionName
                      functionArn
                      vpcConfig {
                        subnetIds
                      }
                    }
                  }
                }
              }
            }'''

    response = client.graphql_execute(query)
    functions = response["aws"]["lambda"]["functionConfiguration"]["data"]

    return [f for f in functions if not f["vpcConfig"] or not f["vpcConfig"]["subnetIds"]]
