import datetime
import json
import hashlib
import uuid

import boto3

from spacetrack import SpaceTrackClient
from spacetrack.base import AuthenticationError
import spacetrack.operators as op

from .__version__ import __version__

HANDLER_SEMVER = __version__

S3 = boto3.client('s3', region_name = 'us-west-2')

def _fmt_error(code: int, message: str, request_id: str):
    return {"statusCode": code, "body": json.dumps({"version": HANDLER_SEMVER, "error": message, "requestID": request_id})}

BUCKET_NAME = "space-track-cache"
DATE_FMT = "%Y-%m-%d"
USAGE = """
{
    "identity": "[YOUR SPACETRACK USERNAME],
    "password": "[YOUR SPACETRACK PASSWORD],
    "date": "YYYY-MM-DD"
}
"""

def query_stc_for_date(client: SpaceTrackClient, dt: datetime.datetime) -> str:
    start_date = dt.date()
    end_date = (dt + datetime.timedelta(days=1)).date()
    date_bounds = op.inclusive_range(start_date, end_date)

    return client.tle(epoch=date_bounds, format='3le', orderby='epoch')  # type: ignore


def _dt_hash(dt: datetime.datetime):
    # We hash the dates to keep the bucket index as flat as possible
    # This speeds access, and minimizes the cost of running the service.
    return hashlib.md5(dt.strftime(DATE_FMT).encode()).hexdigest()


def query_cache_for_date(dt: datetime.datetime):
    try:
        key = S3.get_object(Bucket=BUCKET_NAME, Key=_dt_hash(dt))
    except S3.exceptions.NoSuchKey:
        return None

    return key["Body"].read().decode()


def insert_data_to_cache(tle_data: str, dt: datetime.datetime):
    S3.put_object(Body=tle_data.encode(), Key=_dt_hash(dt))


def hello(event, context, auth_client=SpaceTrackClient, query_call=query_cache_for_date):
    request_id = str(uuid.uuid4())
    print("Started handler for request ID:" + request_id)

    # Request format validation
    try:
        body_json = json.loads(event["body"])
        ident = body_json["identity"]
        passwd = body_json["password"]
        date_string = body_json["date"]
        query_dt = datetime.datetime.strptime(date_string, DATE_FMT)
    except (json.JSONDecodeError, KeyError, ValueError):
        return _fmt_error(400, "Bad Request" + USAGE, request_id)

    # Use ST for auth wrt. to ability to D/L these
    print("Logging in: %s:%s" % (ident, "*" * len(passwd)))
    stc = auth_client(ident, passwd)

    try:
        stc.authenticate()
    except AuthenticationError:
        return _fmt_error(403, "Bad SpaceTrack Credentials", request_id)
    print("Logged in successfully")

    # Check the cache for the date in question
    tle_data = query_call(query_dt)
    cache_hit = tle_data is not None

    if not cache_hit:
        tle_data = query_stc_for_date(stc, query_dt)
        insert_data_to_cache(tle_data, query_dt)

    return {
        "statusCode": 200,
        "body": json.dumps({"tle": tle_data, "cached": cache_hit, "requestID": request_id, "version": HANDLER_SEMVER})
    }
