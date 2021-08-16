import datetime
import json
import os
from posix import environ
from unittest import TestCase

from spacetrack import SpaceTrackClient
from spacetrack.base import AuthenticationError
import pytest

from server import handler


class Auth:
    def __init__(*args, **kwargs):
        pass

class AuthGood(Auth):
    def authenticate(self):
        pass

class AuthBad(Auth):
    def authenticate(self):
        raise AuthenticationError()


class HandlerTests(TestCase):
    def test_auth_success(self):
        event = {"body": json.dumps({"identity": "foo", "password": "bar", "date": "2001-01-01"})}
        response = handler.hello(event, {}, auth_client=AuthGood)
        assert response["statusCode"] == 200
        print(json.loads(response["body"]))
        

    def test_auth_failure(self):
        event = {"body": json.dumps({"identity": "foo", "password": "bar", "date": "2001-01-01"})}
        response = handler.hello(event, {}, auth_client=AuthBad)
        assert response["statusCode"] == 403
        assert "error" in json.loads(response["body"]) 

    
    def test_malformed_date(self):
        event = {"body": json.dumps({"identity": "foo", "password": "bar", "date": "2001-53-01"})}
        response = handler.hello(event, {}, auth_client=AuthGood)
        assert response["statusCode"] == 400
        assert "error" in json.loads(response["body"]) 

    def test_content_correctness(self):
        # The early content that is in the pullthrough cache
        # was generated by out Java client. This test confirms
        # That the content pulled down for a particular day is
        # the same as that pulled down by earlier invocations from Java
        user = os.environ.get("ST_UN")
        password = os.environ.get("ST_PW")

        # Skip this test if we don't have the environment variables
        if (user is None) or (password is None):
            pytest.skip("Skipping test, no crednetials to test with")

        stc = SpaceTrackClient(user, password)
        dt = datetime.datetime(1974, 1, 1)
        expected = handler.query_stc_for_date(stc, dt)
        actual = handler.query_cache_for_date(dt)

        # Do the diff outselves, as if it fails difflib hangs _forever_ on the result :/
        for i, (e, a) in enumerate(zip(expected.splitlines(), actual.splitlines())):
            print(i)
            print("Expected")
            print(e)
            print("Actual")
            print(a)
            assert e == a
