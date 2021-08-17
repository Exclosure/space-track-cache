# space-track-cache
The code that runs the Exclosure pull through TLE cache.

Often we want to do analyses of TLE data that spans many
months/days/years. The API rate limits of space-track.org
makes pulling this sort of data down quite cumbersome.

To speed this up, (and minimize our impact on their servers)
we implemented a lambda+s3 cache for simple TLE queries.

These queries only allow you to pull _all_ of the TLE data
aligned to a particular UTC date, and are cached in s3 and
reused to avoid pulling on space-track.

```
==========        ==============        ===================
| Client |   ==>  | AWS Lambda | <====> | Space-Track.org |
==========        ==============        ===================
                        ^
                        |
                        V
                ==================
                | S3 Cached TLEs |
                ==================
```

At the time of writing the s3 cache has >90% of all days available.
Additionally, the client interface will self-throttle in the unlikely
case where a large number of non cached entities are desired.

## Using the client
Install this module by:
`pip install stcache`

Use it like:
```python
import stcache

un = input("SpaceTrack Username:")
pw = input("SpaceTrack Password:")
date = input("YYYY-MM-DD:")

print(stcache.TLEClient(un, pw).get_tle_for_day(dt))
```

## Server UnitTesting:
```bash
cd server
pytest .
```
