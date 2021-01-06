import itertools
from datetime import datetime, timedelta
from dataclasses import dataclass
from faros.utils import relative_change, get_comparison_windows
from faros.client import FarosClient


@dataclass
class DeployedCommit:
    commit_created_at: datetime
    deployment_ended_at: datetime
    application: str


# TODO: group by environment in addition to application name
def mean_lead_time(deployed_commits):
    """
    Method expects deployed commits to be sorted by application name
    """
    total_lead_time = 0
    total_commits = 0
    for key, app in itertools.groupby(deployed_commits, lambda c: c.application):
        commits = list(app)
        app_lead_time = 0
        for c in commits:
            app_lead_time += (c.deployment_ended_at -
                              c.commit_created_at).total_seconds()
        total_lead_time += app_lead_time
        total_commits += len(commits)
    return (total_lead_time/total_commits) * 1000 if total_commits else None


def extract_deployed_commits(commits):
    deployed_commits = []
    for c in commits:
        for b in c["builds"]["nodes"]:
            for d in b["deployments"]["nodes"]:
                if d["endedAt"] != None:
                    deployed_commits.append(
                        DeployedCommit(
                            commit_created_at=datetime.fromtimestamp(
                                int(c["createdAt"])/1000),
                            deployment_ended_at=datetime.fromtimestamp(
                                int(d["endedAt"])/1000),
                            application=d["application"]["name"]
                        )
                    )
    return deployed_commits


def lambda_handler(event, context):
    client = FarosClient.from_event(event)
    reference_time = int(event["params"].get(
        "reference_time_secs", datetime.now().timestamp()))
    window_size = int(event["params"].get("window_days", 30))
    compare_to = int(event["params"].get("compare_to_days", 7))
    previous_window, current_window = get_comparison_windows(
        datetime.fromtimestamp(reference_time), window_size, compare_to)

    query = '''{
       vcs {
         commits(filter: {createdAt: {greaterThan: "%s"}}) {
           nodes {
             createdAt
             builds {
               nodes {
                 deployments {
                   nodes {
                     endedAt
                     status
                     application {
                       name
                     }
                   }
                 }
               }
             }
           }
         }
       }
    }''' % int(previous_window.since.timestamp() * 1000)

    response = client.graphql_execute(query)
    commits = response["vcs"]["commits"]["nodes"]
    deployed_commits = extract_deployed_commits(commits)
    deployed_commits.sort(key=lambda c: c.application)

    cwd_previous = [
        c for c in deployed_commits if c.commit_created_at in previous_window]
    cwd_current = [
        c for c in deployed_commits if c.commit_created_at in current_window]

    mlt_previous = mean_lead_time(cwd_previous)
    mlt_current = mean_lead_time(cwd_current)

    return {
        "Mean Lead Time": mlt_current,
        "Mean Lead Time Change": relative_change(mlt_current, mlt_previous),
    }
