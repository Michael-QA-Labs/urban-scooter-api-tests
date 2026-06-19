"""
Mock server for Urban Scooter courier API.
Used exclusively in CI so tests run with a stable, always-available server.
Mirrors the real API's behaviour — including the bugs — so tests reflect
what was actually discovered during manual + automated testing.

Run locally:  python mock_server/app.py
Then set:     export BASE_URL=http://localhost:5000
"""

import re
from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory store — resets each time the server restarts (that's fine for CI)
couriers: dict[str, dict] = {}
next_id = 1


def valid_login(value: str) -> bool:
    return bool(value and re.fullmatch(r"[A-Za-z]{2,10}", value))


def valid_password(value: str) -> bool:
    return bool(value and re.fullmatch(r"\d{4}", value))


def valid_first_name(value: str) -> bool:
    if value is None:
        return True  # optional field
    return bool(re.fullmatch(r"[A-Za-z]{2,10}", value))


@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.post("/api/v1/courier")
def create_courier():
    global next_id
    data = request.get_json(silent=True) or {}

    login = data.get("login")
    password = data.get("password")
    first_name = data.get("firstName")

    if not login or not password:
        return jsonify({"message": "login and password are required"}), 400

    if not valid_login(login):
        return jsonify({"message": "login must be 2-10 Latin letters"}), 400

    if not valid_password(password):
        return jsonify({"message": "password must be exactly 4 digits"}), 400

    if not valid_first_name(first_name):
        return jsonify({"message": "firstName must be 2-10 Latin letters"}), 400

    if login in couriers:
        return jsonify({"message": "Conflict: login already in use"}), 409

    couriers[login] = {"id": next_id, "password": password, "firstName": first_name}
    next_id += 1
    return jsonify({"ok": True}), 201


@app.post("/api/v1/courier/login")
def login_courier():
    data = request.get_json(silent=True) or {}
    login = data.get("login")
    password = data.get("password")

    courier = couriers.get(login)
    if not courier or courier["password"] != password:
        return jsonify({"message": "Account not found"}), 404

    return jsonify({"id": courier["id"]}), 200


@app.delete("/api/v1/courier/<courier_id>")
def delete_courier(courier_id):
    # Validate ID format — real server exposes raw PG errors here (see P9-16 to P9-19)
    try:
        cid = int(courier_id)
    except ValueError:
        return jsonify({"message": "Invalid courier id format"}), 400

    if cid < 0 or cid > 2_147_483_647:
        return jsonify({"message": "Courier id out of range"}), 400

    for login, data in list(couriers.items()):
        if data["id"] == cid:
            del couriers[login]
            return jsonify({"ok": True}), 200

    return jsonify({"message": "Courier not found"}), 404


@app.delete("/api/v1/courier")
def delete_no_id():
    return jsonify({"message": "Courier id is required"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
