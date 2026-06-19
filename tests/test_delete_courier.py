import time
import pytest
import requests as req
from jsonschema import validate
from utils.api_client import CourierAPI
from utils.api_client import assert_response_time
from schemas.courier import DELETE_SUCCESS_SCHEMA
from config.settings import VALID_PASSWORD, COURIER_ENDPOINT


@pytest.fixture
def api():
    return CourierAPI()


# ---------------------------------------------------------------------------
# Smoke
# ---------------------------------------------------------------------------

@pytest.mark.smoke
def test_delete_existing_courier_returns_200(api, new_courier):
    courier_id = api.get_id(new_courier["login"], VALID_PASSWORD)
    assert courier_id is not None, "Could not retrieve courier ID via login"
    start = time.time()
    r = api.delete(courier_id)
    assert_response_time(time.time() - start)
    assert r.status_code == 200, (
        f"Expected 200 for valid courier delete, got {r.status_code}. Body: {r.text}"
    )
    validate(instance=r.json(), schema=DELETE_SUCCESS_SCHEMA)


# ---------------------------------------------------------------------------
# Negative
# ---------------------------------------------------------------------------

@pytest.mark.negative
@pytest.mark.parametrize("courier_id,description", [
    ("abc",          "alphabetic id"),
    ("12.5",         "decimal id"),
    ("99999999999",  "integer overflow id"),
    ("-1",           "negative id"),
])
def test_delete_invalid_id_format_returns_400(api, courier_id, description):
    start = time.time()
    r = api.delete(courier_id)
    assert_response_time(time.time() - start)
    assert r.status_code == 400, (
        f"[{description}] Expected 400, got {r.status_code}. Body: {r.text}"
    )


@pytest.mark.negative
def test_delete_nonexistent_courier_returns_404(api):
    start = time.time()
    r = api.delete(999999)
    assert_response_time(time.time() - start)
    assert r.status_code == 404, (
        f"Expected 404 for nonexistent courier, got {r.status_code}. Body: {r.text}"
    )


@pytest.mark.negative
def test_delete_without_id_returns_405_or_404(api):
    start = time.time()
    r = req.delete(COURIER_ENDPOINT)
    assert_response_time(time.time() - start)
    assert r.status_code in (404, 405), (
        f"Expected 404 or 405 with no ID, got {r.status_code}. Body: {r.text}"
    )
