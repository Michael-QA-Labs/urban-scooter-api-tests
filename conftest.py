import random
import string
import pytest
from utils.api_client import CourierAPI
from config.settings import VALID_PASSWORD, VALID_FIRSTNAME


def unique_login() -> str:
    """Generate a unique 8-char Latin-letters-only login (satisfies 2-10 char rule)."""
    return "T" + "".join(random.choices(string.ascii_lowercase, k=7))


@pytest.fixture(scope="function")
def api():
    """Return a fresh CourierAPI client for each test."""
    return CourierAPI()


@pytest.fixture(scope="function")
def new_courier(api):
    """
    Create a courier before the test, yield its credentials,
    then clean up after — even if the test fails.
    """
    login = unique_login()
    password = VALID_PASSWORD
    first_name = VALID_FIRSTNAME

    response = api.create(login, password, first_name)
    assert response.status_code == 201, (
        f"Fixture setup failed — could not create courier. "
        f"Status: {response.status_code}, Body: {response.text}"
    )

    yield {"login": login, "password": password, "firstName": first_name}

    courier_id = api.get_id(login, password)
    if courier_id:
        api.delete(courier_id)
