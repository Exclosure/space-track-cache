# space-track-cache
This is the code that runs the Exclosure pull-through TLE cache.

Often we want to do analyses of TLE data that spans many
months/days/years. The API rate limits of space-track.org
makes pulling this sort of data down quite cumbersome.

To speed this up, (and minimize our impact on their servers)
we implemented a lambda+s3 cache for simple TLE queries.

These queries only allow you to pull _all_ of the TLE data
aligned to a particular UTC date, and are cached in s3 and
reused to avoid pulling on space-track.

To break this down concretely the following diagram:

```
========== --1--> ==============        ===================
| Client |        | AWS Lambda | <--3-- | Space-Track.org |
========== <--5-- ==============        ===================
                     ^    |
                     |    4
                     2    |
                     |    V
                ==================
                | S3 Cached TLEs |
                ==================
```

1. The client requests TLE data for a particular day
2. The lambda attempts to pull data from the cache
3. If it isn't present in the cache, it pulls it from space-track
4. The TLE data from space track is inserted in the cache
5. The TLE data is returned to the request maker


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

print(stcache.TLEClient(un, pw).get_tle_for_day(2001, 1, 1))
```

## Server UnitTesting:
```bash
cd server
pytest .
```
