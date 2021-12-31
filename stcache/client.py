#!/usr/bin/env python3
"""Client for interacting with TLE cache."""
import datetime
import os
import textwrap
import time
from getpass import getpass

import requests
from rush.limiters.periodic import PeriodicLimiter
from rush.quota import Quota
from rush.stores.dictionary import DictionaryStore as RushDictionaryStore
from rush.throttle import Throttle

ST_CACHE_URL = "https://api.txcl.io/tle/day"
DATE_FMT = "%Y-%m-%d"

_UTC = datetime.timezone.utc


class TLEClientError(RuntimeError):
    """Class for errors related to TLE client."""


class TLEClient:
    """Main TLE API."""

    def __init__(self, identity: str, password: str):
        """Initialize the client.

        Arguments:
            identity: A SpaceTrack.org username.
            password: A SpaceTrack.org password.
        """
        self._ident = identity
        self._pass = password

        self._cache = {}

        # Query limiter
        rush_store = RushDictionaryStore()  # type: ignore
        limiter = PeriodicLimiter(rush_store)
        self._rpm_throttle = Throttle(limiter=limiter, rate=Quota.per_minute(30))
        self._rph_throttle = Throttle(limiter=limiter, rate=Quota.per_hour(300))

        self._next_request = time.time()

    def _ratelimit_pause(self):
        """Perform get request, handling rate limiting."""
        minute_limit = self._rpm_throttle.check("st_min_key", 1)
        hour_limit = self._rph_throttle.check("st_hour_key", 1)

        sleep_time = 0

        if minute_limit.limited:
            sleep_time = minute_limit.retry_after.total_seconds()

        if hour_limit.limited:
            sleep_time = max(sleep_time, hour_limit.retry_after.total_seconds())

        self._next_request = time.time() + sleep_time

        if sleep_time > 0:
            time.sleep(sleep_time)

    def get_tle_for_dt(self, dt: datetime.datetime, use_cache=True) -> str:
        """Get the TLE data for a date given by the datetime in UTC."""
        if not _tz_aware(dt):
            raise TLEClientError(
                textwrap.dedent(
                    f"""
                Datetime dt must be timezone-aware but
                found dt.tzinfo={dt.tzinfo}. If this date was
                specified in UTC without a timezone, consider
                localizing via

                    dt = dt.replace(tzinfo=datetime.timezone.utc)

                If the date is in some other timezone, convert
                to UTC prior to calling this function.
                """
                )
            )

        if not dt.tzinfo.utcoffset != 0:
            # This could be a warning, but timezone issues cause so
            # many problems, let's keep it an error.
            raise TLEClientError(
                f"Timezone must be in UTC, but got dt.tzinfo={dt.tzinfo}."
            )

        date_key = dt.strftime(DATE_FMT)

        if use_cache and date_key in self._cache:
            return self._cache[date_key]

        request = {
            "identity": self._ident,
            "password": self._pass,
            "date": date_key,
        }
        response = requests.post(ST_CACHE_URL, json=request)
        if not response.ok:
            raise TLEClientError(f"Invalid response for {date_key}: {response}")
        resp_json = response.json()

        if "error" in resp_json:
            raise TLEClientError(
                f"Error in TLE data for {date_key}: {resp_json['error']}"
            )

        if not resp_json.get("cached"):
            self._ratelimit_pause()

        if "tle" not in resp_json:
            raise TLEClientError(f"No TLE data for {date_key}: {resp_json}")

        self._cache[date_key] = resp_json["tle"]
        return self._cache[date_key]

    def get_tle_for_day(self, year: int, month: int, day: int, use_cache=True):
        """Get the TLE for a given day in UTC."""
        return self.get_tle_for_dt(
            datetime.datetime(year, month, day, tzinfo=_UTC), use_cache=use_cache
        )


def main():
    """Command-line interface to this tool."""
    username = os.environ.get("SPACETRACK_USERNAME") or input(
        "SpaceTrack.org username:"
    )
    password = os.environ.get("SPACETRACK_PASSWORD") or getpass(
        "SpaceTrack.org password:"
    )
    date = "2000-01-01" or input("YYYY-MM-DD:")
    dt = datetime.datetime.strptime(date, DATE_FMT)
    dt_utc = dt.astimezone(tz=datetime.timezone.utc)
    print(TLEClient(username, password).get_tle_for_dt(dt_utc))


def _tz_aware(dt: datetime.datetime) -> bool:
    """Check if the datetime is timezone-aware.

    https://docs.python.org/3/library/datetime.html#determining-if-an-object-is-aware-or-naive
    """
    return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None


if __name__ == "__main__":
    main()
