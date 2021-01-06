import itertools
from datetime import datetime, timedelta
from faros.utils import relative_change, get_comparison_windows
from faros.client import FarosClient


# TODO: Group by environment in addition to app name
def mean_cycle_time(successful_deploys):
    """
    Method expects successful deployments sorted by the application name and the end-time of the deployment
    """
    span = 0
    successive_deploys = 0
    for key, app in itertools.groupby(successful_deploys, lambda d: d["application"]["name"]):
        deploys = list(app)
        if len(deploys) > 1:
            span += int(deploys[-1]["endedAt"]) - int(deploys[0]["endedAt"])
            successive_deploys += len(deploys) - 1
    return span/successive_deploys if successive_deploys else None


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

    query = '''{
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
    }''' % int(previous_window.since.timestamp() * 1000)

    response = client.graphql_execute(query)
    deploys = [d for d in response["cicd"]["deployments"]["nodes"]
               if d.get("endedAt") is not None and d["status"] == "Success"]
    deploys.sort(key=lambda d: (d["application"]["name"], d["endedAt"]))

    deploys_previous = filter_deploys(deploys, previous_window)
    deploys_current = filter_deploys(deploys, current_window)

    mct_previous = mean_cycle_time(deploys_previous)
    mct_current = mean_cycle_time(deploys_current)

    return {
        "Mean Cycle Time": mct_current,
        "Mean Cycle Time Change": relative_change(mct_current, mct_previous),
    }
