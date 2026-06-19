import requests
from config.settings import COURIER_ENDPOINT, COURIER_LOGIN_ENDPOINT


class CourierAPI:
    """
    Thin wrapper around the Urban Scooter courier endpoints.
    Tests call methods here — never raw requests.post() directly.
    This makes the suite easier to maintain and refactor.
    """

    def create(self, login: str, password: str, first_name: str = None) -> requests.Response:
        payload = {"login": login, "password": password}
        if first_name is not None:
            payload["firstName"] = first_name
        return requests.post(COURIER_ENDPOINT, json=payload)

    def login(self, login: str, password: str) -> requests.Response:
        return requests.post(
            COURIER_LOGIN_ENDPOINT,
            json={"login": login, "password": password}
        )

    def delete(self, courier_id: int) -> requests.Response:
        return requests.delete(f"{COURIER_ENDPOINT}/{courier_id}")

    def get_id(self, login: str, password: str) -> int | None:
        """Login and return the courier id — used for cleanup in fixtures."""
        response = self.login(login, password)
        if response.status_code == 200:
            return response.json().get("id")
        return None
