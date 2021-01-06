import itertools
from datetime import datetime, timedelta
from faros.utils import relative_change, get_comparison_windows
from faros.client import FarosClient


# TODO: Group by environment in addition to app name
def mean_recovery_time(deployments):
    """
    Method expects deployments sorted by the application name and the end-time of the deployment
    """
    total_recovery_time = 0
    total_recoveries = 0
    for key, app in itertools.groupby(deployments, lambda d: d["application"]["name"]):
        deploys = list(app)
        app_recovery_time = 0
        app_recoveries = 0
        i = 0
        while i < len(deploys):
            if deploys[i]["status"] == "Failed":
                failure_time = int(deploys[i]["endedAt"])
                for j in range(i+1, len(deploys)):
                    if deploys[j]["status"] == "Success":
                        success_time = int(deploys[j]["endedAt"])
                        app_recovery_time += success_time - failure_time
                        app_recoveries += 1
                        i = j
                        break
            i += 1
        if app_recoveries > 0:
            total_recovery_time += app_recovery_time
            total_recoveries += app_recoveries
    return total_recovery_time/total_recoveries if total_recoveries else None


def filter_deploys(deploys, window):
    return [d for d in deploys
            if datetime.fromtimestamp(int(d["endedAt"])/1000) in window]


def lambda_handler(event, context):
    client = FarosClient.from_event(event)
    reference_time = int(event["params"].get(
        "reference_time_secs", datetime.now().timestamp()))
    window_size = int(event["params"].get("window_days", 30))
    compare_to = int(event["params"].get("compare_to_days", 7))
    previous_window, current_window = get_comparison_windows(
        datetime.fromtimestamp(reference_time), window_size, compare_to)

    query = """{
      cicd {
        deployments(filter: {startedAt: {greaterThan: "%s"}}) {
	        nodes {
            endedAt
            startedAt
            status
            application {
              name
            }
          }
        }
      }
    }""" % int(previous_window.since.timestamp() * 1000)

    response = client.graphql_execute(query)
    deploys = [d for d in response["cicd"]["deployments"]["nodes"]
               if d.get("endedAt") is not None]
    deploys.sort(key=lambda d: (d["application"]["name"], d["endedAt"]))

    deploys_previous = filter_deploys(deploys, previous_window)
    deploys_current = filter_deploys(deploys, current_window)

    mrt_previous = mean_recovery_time(deploys_previous)
    mrt_current = mean_recovery_time(deploys_current)

    return {
        "Mean Time to Recovery": mrt_current,
        "Mean Recovery Time Change": relative_change(mrt_current, mrt_previous),
    }
