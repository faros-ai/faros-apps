from faros.client import FarosClient
from faros.utils import time_diff


def is_stale_branch(b, cutoff):
    if b["commit"]:
        return time_diff(b["commit"]["date"]).days > cutoff
    else:
        return False


def lambda_handler(event, context):
    client = FarosClient.from_event(event)

    query = '''{
              github {
                repository {
                  data {
                    name
                    branches {
                      data {
                        name
                        repo_name
                        commit_sha
                        protected
                        commit {
                          sha
                          date
                        }
                      }
                    }
                  }
                }
              }
            }'''

    response = client.graphql_execute(query)
    repos = response["github"]["repository"]["data"]
    cutoff = int(event["params"]["max_days"])

    return [
        b for repo in repos for b in repo["branches"]["data"]
        if is_stale_branch(b, cutoff)
    ]
