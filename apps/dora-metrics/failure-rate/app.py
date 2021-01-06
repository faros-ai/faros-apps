import itertools
from datetime import datetime, timedelta
from faros.utils import relative_change, get_comparison_windows
from faros.client import FarosClient


# TODO: Group by environment in addition to app name
def mean_time_between_failures(failed_deploys):
    """
    Method expects failed deployments to be sorted by application name and end-time of deployment
    """
    span = 0
    successive_deploys = 0
    for key, app in itertools.groupby(failed_deploys, lambda d: d["application"]["name"]):
        deploys = list(app)
        if len(deploys) > 1:
            span += int(deploys[-1]["endedAt"]) - int(deploys[0]["endedAt"])
            successive_deploys += len(deploys) - 1
    return span/successive_deploys if successive_deploys else None


def failure_rate(failed_deploys, successful_deploys):
    total = len(failed_deploys) + len(successful_deploys)
    return len(failed_deploys)/total if total else None


def filter_deploys(deploys, status, window):
    return [d for d in deploys
            if d["status"] == status and datetime.fromtimestamp(int(d["endedAt"])/1000) in window]


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

    failed_deploys_prev = filter_deploys(deploys, "Failed", previous_window)
    failed_deploys_curr = filter_deploys(deploys, "Failed", current_window)

    success_deploys_prev = filter_deploys(deploys, "Success", previous_window)
    success_deploys_curr = filter_deploys(deploys, "Success", current_window)

    mtbf_prev = mean_time_between_failures(failed_deploys_prev)
    mtbf_curr = mean_time_between_failures(failed_deploys_curr)

    fr_prev = failure_rate(failed_deploys_prev, success_deploys_prev)
    fr_curr = failure_rate(failed_deploys_curr, success_deploys_curr)

    return {
        "Change Failure Rate": fr_curr,
        "Change Failure Rate Change": relative_change(fr_curr, fr_prev),
        "Mean Time between Failures": mtbf_curr,
        "Mean Time between Failures Change": relative_change(mtbf_curr, mtbf_prev)
    }
