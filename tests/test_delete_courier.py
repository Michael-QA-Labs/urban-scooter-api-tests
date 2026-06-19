import pytest
from jsonschema import validate
from utils.api_client import CourierAPI
from schemas.courier import DELETE_SUCCESS_SCHEMA
from config.settings import VALID_PASSWORD


@pytest.fixture
def api():
    return CourierAPI()


# ---------------------------------------------------------------------------
# Smoke
# ---------------------------------------------------------------------------

@pytest.mark.smoke
def test_delete_existing_courier_returns_200(api, new_courier):
    """
    Known bug (P9-15): DELETE returns 404 for a courier that was
    just confirmed to exist via login. This test documents the
    expected behaviour per requirements.
    """
    courier_id = api.get_id(new_courier["login"], VALID_PASSWORD)
    assert courier_id is not None, "Could not retrieve courier ID via login"

    r = api.delete(courier_id)
    assert r.status_code == 200, (
        f"Expected 200 for valid courier delete, got {r.status_code}. "
        f"Body: {r.text} — See Jira P9-15"
    )
    validate(instance=r.json(), schema=DELETE_SUCCESS_SCHEMA)


# ---------------------------------------------------------------------------
# Negative — invalid ID formats (all exposed the 500 + raw PG error bug)
# ---------------------------------------------------------------------------

@pytest.mark.negative
@pytest.mark.parametrize("courier_id,description", [
    ("abc",    "alphabetic id"),
    ("12.5",   "decimal id"),
    ("99999999999", "integer overflow id"),
    ("-1",     "negative id"),
])
def test_delete_invalid_id_format_returns_400(api, courier_id, description):
    """
    Known bug (P9-16 to P9-19): These return HTTP 500 with raw
    PostgreSQL error messages instead of a proper 400 Bad Request.
    Tests document expected vs actual behaviour.
    """
    r = api.delete(courier_id)
    assert r.status_code == 400, (
        f"[{description}] Expected 400, got {r.status_code}. "
        f"Body: {r.text} — Raw DB error exposed to client (see Jira)"
    )


@pytest.mark.negative
def test_delete_nonexistent_courier_returns_404(api):
    """Deleting a courier ID that doesn't exist should return 404."""
    r = api.delete(999999)
    assert r.status_code == 404, (
        f"Expected 404 for nonexistent courier, got {r.status_code}. Body: {r.text}"
    )


@pytest.mark.negative
def test_delete_without_id_returns_405_or_404(api):
    """DELETE /api/v1/courier with no ID — should not be 200."""
    import requests
    from config.settings import COURIER_ENDPOINT
    r = requests.delete(COURIER_ENDPOINT)
    assert r.status_code in (404, 405), (
        f"Expected 404 or 405 with no ID, got {r.status_code}. Body: {r.text}"
    )
