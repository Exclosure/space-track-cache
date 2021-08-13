import datetime
import json

from spacetrack import SpaceTrackClient
from spacetrack.base import AuthenticationError


def _fmt_error(code: int, message: str):
    return {"statusCode": code, "body": json.dumps({"error": message})}


def hello(event, context):
    body_json = json.loads(event["body"])

    stc = SpaceTrackClient(body_json["identity"], body_json["password"])

    try:
        stc.authenticate()
    except AuthenticationError:
        return _fmt_error(403, "Bad SpaceTrack Credentials")

    try:
        target_date = datetime.datetime.strptime(body_json["date"], "%Y-%m-%d")
    except ValueError:
        return _fmt_error(400, "Malformed Date")

    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    return {
        "statusCode": 200,
        "body": json.dumps(body)
    }
