import itertools

from faros.client import FarosClient
from faros.utils import time_diff


def has_recent_activity(user, cutoff):
    commits = (c["date"] for c in user["commits"]["data"])
    issues = (i["updated_at"] for i in user["issues"]["data"])
    prs = (p["updated_at"] for p in user["pullRequests"]["data"])
    for activity_date in itertools.chain(commits, issues, prs):
        if time_diff(activity_date).days < cutoff:
            return True
    return False


def lambda_handler(event, context):
    client = FarosClient.from_event(event)
    cutoff = int(event["params"]["max_days"])

    query = '''{
              github {
                user {
                  data {
                    login
                    name
                    email
                    membership
                    commits {
                      data {
                        sha
                        date
                      }
                    }
                    issues {
                      data {
                        state
                        updated_at
                      }
                    }
                    pullRequests {
                      data {
                        state
                        updated_at
                      }
                    }
                  }
                }
              }
            }'''

    response = client.graphql_execute(query)
    users = response["github"]["user"]["data"]

    return [
        {
            "login": u["login"],
            "name": u["name"],
            "email": u["email"],
            "membership": u["membership"]
        }
        for u in users if not has_recent_activity(u, cutoff)
    ]
