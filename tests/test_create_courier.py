import time
import random
import string
import pytest
from jsonschema import validate
from utils.api_client import CourierAPI
from schemas.courier import CREATE_SUCCESS_SCHEMA, ERROR_SCHEMA
from config.settings import VALID_LOGIN, VALID_PASSWORD, VALID_FIRSTNAME, RESPONSE_TIME_LIMIT_SECONDS


def unique_login():
    return "T" + "".join(random.choices(string.ascii_lowercase, k=7))


@pytest.fixture(autouse=False)
def api():
    return CourierAPI()


# ---------------------------------------------------------------------------
# Smoke — the happy path must pass before anything else matters
# ---------------------------------------------------------------------------

@pytest.mark.smoke
def test_create_courier_returns_201(api):
    login = unique_login()
    start = time.time()
    r = api.create(login, VALID_PASSWORD, VALID_FIRSTNAME)
    elapsed = time.time() - start

    assert r.status_code == 201
    assert elapsed < RESPONSE_TIME_LIMIT_SECONDS, f"Response too slow: {elapsed:.2f}s"
    validate(instance=r.json(), schema=CREATE_SUCCESS_SCHEMA)
    assert r.json()["ok"] is True

    # cleanup
    courier_id = api.get_id(login, VALID_PASSWORD)
    if courier_id:
        api.delete(courier_id)


@pytest.mark.smoke
def test_create_courier_without_firstname_returns_201(api):
    """firstName is optional per requirements."""
    login = unique_login()
    r = api.create(login, VALID_PASSWORD)
    assert r.status_code == 201

    courier_id = api.get_id(login, VALID_PASSWORD)
    if courier_id:
        api.delete(courier_id)


# ---------------------------------------------------------------------------
# Regression — login field boundary value analysis
# ---------------------------------------------------------------------------

@pytest.mark.regression
@pytest.mark.parametrize("login,expected_status", [
    ("Ab",           201),   # min length 2 — valid
    ("Abcdefghij",   201),   # max length 10 — valid
    ("A",            400),   # below min — invalid
    ("Abcdefghijk",  400),   # above max — invalid
])
def test_create_courier_login_length_boundaries(api, login, expected_status):
    r = api.create(login, VALID_PASSWORD, VALID_FIRSTNAME)
    assert r.status_code == expected_status, (
        f"login='{login}' → expected {expected_status}, got {r.status_code}. Body: {r.text}"
    )
    if r.status_code == 201:
        courier_id = api.get_id(login, VALID_PASSWORD)
        if courier_id:
            api.delete(courier_id)


@pytest.mark.regression
@pytest.mark.parametrize("login", [
    "Иван",       # Cyrillic
    "Mike1",      # digit in login
    "Mike!",      # special character
    "mike garcia",# space
    "",           # empty string
])
def test_create_courier_login_invalid_characters(api, login):
    """Login must be Latin letters only — all these should be rejected."""
    r = api.create(login, VALID_PASSWORD, VALID_FIRSTNAME)
    assert r.status_code == 400, (
        f"login='{login}' should be rejected (400), got {r.status_code}. Body: {r.text}"
    )


# ---------------------------------------------------------------------------
# Regression — password field boundary value analysis
# ---------------------------------------------------------------------------

@pytest.mark.regression
@pytest.mark.parametrize("password,expected_status", [
    ("1234",  201),   # exactly 4 digits — valid
    ("123",   400),   # below min — invalid
    ("12345", 400),   # above max — invalid
    ("abcd",  400),   # letters not allowed
    ("12.4",  400),   # decimal not allowed
])
def test_create_courier_password_validation(api, password, expected_status):
    login = unique_login()
    r = api.create(login, password, VALID_FIRSTNAME)
    assert r.status_code == expected_status, (
        f"password='{password}' → expected {expected_status}, got {r.status_code}. Body: {r.text}"
    )
    if r.status_code == 201:
        courier_id = api.get_id(login, password)
        if courier_id:
            api.delete(courier_id)


# ---------------------------------------------------------------------------
# Negative — duplicate courier
# ---------------------------------------------------------------------------

@pytest.mark.negative
def test_create_duplicate_courier_returns_409(api, new_courier):
    """Creating a courier with an existing login must return 409 Conflict."""
    r = api.create(
        new_courier["login"],
        new_courier["password"],
        new_courier["firstName"]
    )
    assert r.status_code == 409, (
        f"Duplicate courier should return 409, got {r.status_code}. Body: {r.text}"
    )


# ---------------------------------------------------------------------------
# Negative — missing required fields
# ---------------------------------------------------------------------------

@pytest.mark.negative
@pytest.mark.parametrize("payload", [
    {"password": VALID_PASSWORD},                        # missing login
    {"login": VALID_LOGIN},                              # missing password
    {},                                                  # missing both
])
def test_create_courier_missing_required_fields(api, payload):
    import requests
    from config.settings import COURIER_ENDPOINT
    r = requests.post(COURIER_ENDPOINT, json=payload)
    assert r.status_code == 400, (
        f"Missing required fields should return 400, got {r.status_code}. Body: {r.text}"
    )
