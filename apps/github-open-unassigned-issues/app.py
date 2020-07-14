from faros.client import FarosClient


def lambda_handler(event, context):
    client = FarosClient.from_event(event)

    query = '''{
              github {
                issue {
                  data {
                    number                
                    title
                    state
                    repo_name
                    created_at
                    labels {
                      name
                    }
                    comments
                    assignee_login
                    pull_request {
                      url
                    }
                  }
                }
              }
            }'''

    response = client.graphql_execute(query)
    issues = response["github"]["issue"]["data"]

    return [
        i for i in issues
        if i["state"] == "open" and not i.get("labels") and not i.get("assignee_login") and not i.get("pull_request")
    ]
