from faros.client import FarosClient
from dataclasses import dataclass
from datetime import datetime, timedelta
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class DeployStages:
    id: str
    application: str
    ended_at: int
    pr_review_time: int
    pr_merge_time: int
    build_time: int
    deploy_time: int

    # TODO: Update pr_review_time and pr_merge_time calculations once approvals are available
    # TODO: Should we be adding null checks for every field here, like the one for the mergedPullRequest?
    def __init__(self, deployment):
        self.id = deployment["id"]
        self.application = deployment["application"]["name"]
        self.ended_at = int(deployment["endedAt"])
        self.pr_review_time = None
        pr = deployment["build"]["commit"]["mergedPullRequest"]
        self.pr_merge_time = int(pr["mergedAt"]) - \
            int(pr["createdAt"]) if pr else None
        self.build_time = int(deployment["build"]["endedAt"]) - \
            int(deployment["build"]["startedAt"])
        self.deploy_time = int(
            deployment["endedAt"]) - int(deployment["startedAt"])


def lambda_handler(event, context):
    client = FarosClient.from_event(event)
    start_time = int(event["params"].get(
        "start_time_secs", (datetime.now()-timedelta(days=30)).timestamp()))
    end_time = int(event["params"].get(
        "end_time_secs", datetime.now().timestamp()))

    query = '''{
      cicd {
        deployments(filter: {startedAt: {greaterThan: "%s"}, endedAt: {lessThan: "%s"}}) {
          nodes {
            id
            status
            startedAt
            endedAt
            application {
              name
            }
            build {
              startedAt
              endedAt
              commit {
                createdAt
                mergedPullRequest {
                  createdAt
                  mergedAt
                }
              }
            }
          }
        }
      }
    }''' % (start_time * 1000, end_time * 1000)

    response = client.graphql_execute(query)
    deployments = [d for d in response["cicd"]["deployments"]["nodes"]
                   if d.get("endedAt") is not None and d["status"] == "Success"]
    deployments.sort(key=lambda d: d["endedAt"])
    breakdown = [DeployStages(d) for d in deployments]

    return [b.to_dict() for b in breakdown]
