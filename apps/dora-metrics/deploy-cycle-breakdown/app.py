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

    def __init__(self, deployment):
        self.id = deployment["id"]
        self.application = deployment["application"]["name"]
        self.ended_at = int(deployment["endedAt"])
        commits = [
            node["commit"]
            for node in deployment["build"]["commitAssociations"]["nodes"]
        ]
        commits.sort(key=lambda c: c["createdAt"])
        last_commit = commits[-1]
        pr = last_commit["mergedPullRequest"]
        approvals = [
            r for r in pr["reviews"]["nodes"]
            if r["state"] == "approved"
        ] if pr else None
        if approvals:
            approvals.sort(key=lambda a: a["submittedAt"])
            first_approval = approvals[0]
            self.pr_review_time = \
                int(first_approval["submittedAt"]) - int(pr["createdAt"])
            self.pr_merge_time = \
                int(pr["mergedAt"]) - int(first_approval["submittedAt"])
        else:
            self.pr_merge_time = \
                int(pr["mergedAt"]) - int(pr["createdAt"]) if pr else None
            self.pr_review_time = None
        self.build_time = int(deployment["build"]["endedAt"]) - \
            int(deployment["build"]["startedAt"])
        self.deploy_time = \
            int(deployment["endedAt"]) - int(deployment["startedAt"])


def lambda_handler(event, context):
    client = FarosClient.from_event(event)
    start_time = int(
        event["params"].get(
            "start_time_secs", (datetime.now() -
                                timedelta(days=30)).timestamp()
        )
    )
    end_time = int(event["params"].get(
        "end_time_secs", datetime.now().timestamp()))

    query = """{
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
              commitAssociations {
                nodes {
                  commit {
                    createdAt
                    mergedPullRequest {
                      createdAt
                      mergedAt
                      reviews {
                        nodes {
                          state
                          submittedAt
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }""" % (
        start_time * 1000,
        end_time * 1000,
    )

    response = client.graphql_execute(query)
    deployments = [
        d
        for d in response["cicd"]["deployments"]["nodes"]
        if d.get("endedAt") is not None and d["status"] == "Success"
    ]
    deployments.sort(key=lambda d: d["endedAt"])
    breakdown = [DeployStages(d) for d in deployments]

    return [b.to_dict() for b in breakdown]
