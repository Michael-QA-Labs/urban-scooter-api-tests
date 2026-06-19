import os

# In CI: BASE_URL is set as a GitHub Actions env var pointing to the mock server
# Locally: falls back to your live TripleTen server URL
BASE_URL = os.getenv(
    "BASE_URL",
    "https://cnt-74e11e23-623e-43bd-b156-e4d77c211212.containerhub.tripleten-services.com"
)

COURIER_ENDPOINT = f"{BASE_URL}/api/v1/courier"
COURIER_LOGIN_ENDPOINT = f"{BASE_URL}/api/v1/courier/login"

VALID_LOGIN = "Mike"
VALID_PASSWORD = "1234"
VALID_FIRSTNAME = "Alex"

RESPONSE_TIME_LIMIT_SECONDS = 2.0
