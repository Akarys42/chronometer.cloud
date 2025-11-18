import datetime

import aiohttp
from pydantic.main import BaseModel

from backend.constants import (
    CLOUDFLARE_ACCOUNT_ID,
    CLOUDFLARE_API_TOKEN,
    CLOUDFLARE_GRAPHQL_ENDPOINT,
)

DATA_QUERY = """
query rumData(
    $accountTag: string!, $now: Time, $shortSampling: Time, $longSampling: Time, $hosts: [string!]
  ) {
  viewer {
    accounts(filter: {accountTag: $accountTag}) {
      shortPathData: rumPageloadEventsAdaptiveGroups(
        filter: {datetime_lt: $now, datetime_geq: $shortSampling, requestHost_in: $hosts, bot: 0}
        limit: 10000
      ) {
        count
        dimensions {
          requestHost
          requestPath
        }
      }

      longPathData: rumPageloadEventsAdaptiveGroups(
        filter: {
          datetime_lt: $shortSampling, datetime_geq: $longSampling, requestHost_in: $hosts, bot: 0
        }
        limit: 10000
      ) {
        count
        dimensions {
          requestHost
          requestPath
        }
      }

      originData: rumPageloadEventsAdaptiveGroups(
        filter: {datetime_lt: $now, datetime_geq: $longSampling, requestHost_in: $hosts, bot: 0},
        limit: 10000
      ) {
        count
        dimensions {
          requestHost
          date
        }
      }
    }
  }
}
"""

FILTERED_PATHS = ["/", "/admin", "/favicon.ico", "/robots.txt"]


class RUMAnalytics(BaseModel):
    """RUM analytics data model."""

    per_path: dict[str, dict[str, int]]
    origin_over_time: dict[str, dict[str, int]]


async def retrieve_rum_analytics(hosts: list[str]) -> RUMAnalytics:
    """Retrieve RUM analytics path data for the specified hosts."""
    if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
        raise EnvironmentError("RUM analytics configuration is missing.")

    now = datetime.datetime.now(datetime.timezone.utc)
    short_sampling = now - datetime.timedelta(days=7)
    long_sampling = now - datetime.timedelta(days=90)

    variables = {
        "accountTag": CLOUDFLARE_ACCOUNT_ID,
        "now": now.isoformat(),
        "shortSampling": short_sampling.isoformat(),
        "longSampling": long_sampling.isoformat(),
        "hosts": hosts,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            CLOUDFLARE_GRAPHQL_ENDPOINT,
            json={"query": DATA_QUERY, "variables": variables},
            headers={
                "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
                "Content-Type": "application/json",
            },
        ) as resp:
            response = await resp.json()

    per_path: dict[str, dict[str, int]] = {}

    short_data = response["data"]["viewer"]["accounts"][0]["shortPathData"]
    long_data = response["data"]["viewer"]["accounts"][0]["longPathData"]

    for entry in short_data:
        host = entry["dimensions"]["requestHost"]
        path = entry["dimensions"]["requestPath"]
        count = entry["count"]

        if host not in per_path:
            per_path[host] = {}

        if path not in per_path[host]:
            per_path[host][path] = 0

        per_path[host][path] += count

    for entry in long_data:
        host = entry["dimensions"]["requestHost"]
        path = entry["dimensions"]["requestPath"]
        count = entry["count"]

        if host not in per_path:
            per_path[host] = {}

        if path not in per_path[host]:
            per_path[host][path] = 0

        per_path[host][path] += count

    for host in per_path:
        for path in FILTERED_PATHS:
            if path in per_path[host]:
                del per_path[host][path]

    origin_over_time: dict[str, dict[str, int]] = {}

    origin_data = response["data"]["viewer"]["accounts"][0]["originData"]
    for entry in origin_data:
        host = entry["dimensions"]["requestHost"]
        date = entry["dimensions"]["date"]
        count = entry["count"]

        if host not in origin_over_time:
            origin_over_time[host] = {}

        origin_over_time[host][date] = count

    return RUMAnalytics(per_path=per_path, origin_over_time=origin_over_time)
