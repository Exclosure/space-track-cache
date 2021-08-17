#!/usr/bin/env python3

import datetime
import requests
import time

from rush.quota import Quota
from rush.throttle import Throttle
from rush.limiters.periodic import PeriodicLimiter
from rush.stores.dictionary import DictionaryStore as RushDictionaryStore


ST_CACHE_URL = "https://api.txcl.io/tle/day"
DATE_FMT = "%Y-%m-%d"

class TLEClient:
    def __init__(self, identity: str, password: str):
        self._ident = identity
        self._pass = password

        # Query limiter
        rush_store = RushDictionaryStore()
        limiter = PeriodicLimiter(rush_store)
        self._rpm_throttle = Throttle(limiter=limiter, rate=Quota.per_minute(30))
        self._rph_throttle = Throttle(limiter=limiter, rate=Quota.per_hour(300))

    def _ratelimit_pause(self):
        """Perform get request, handling rate limiting."""
        minute_limit = self._rpm_throttle.check("st_min_key", 1)
        hour_limit = self._rph_throttle.check("st_hour_key", 1)

        sleep_time = 0

        if minute_limit.limited:
            sleep_time = minute_limit.retry_after.total_seconds()

        if hour_limit.limited:
            sleep_time = max(sleep_time, hour_limit.retry_after.total_seconds())

        if sleep_time > 0:
            time.sleep(sleep_time)


    def get_tle_for_day(self, dt: datetime.datetime):
        request = {
            "identity": self._ident,
            "password": self._pass,
            "date": dt.strftime(DATE_FMT)
        }
        resp_json = requests.post(ST_CACHE_URL, json=request).json()
        print(resp_json)
        if not resp_json["cached"]:
            self._ratelimit_pause()
        
        return resp_json["tle"]

if __name__ == "__main__":
    import os
    un = os.environ["ST_UN"] or input("ST Username:")
    pw = os.environ["ST_PW"] or input("ST Password:")
    date = "2000-01-01" or input("YYYY-MM-DD:")
    dt = datetime.datetime.strptime(date, DATE_FMT)

    print(TLEClient(un, pw).get_tle_for_day(dt))
