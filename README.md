# Urban Scooter — Backend API Test Suite

![CI](https://github.com/mgcg4725-maker/urban-scooter-api-tests/actions/workflows/test.yml/badge.svg)

Automated backend API test suite for the Urban Scooter courier management system. Built with Python, pytest, and GitHub Actions CI.

---

## What this tests

The Urban Scooter platform exposes a REST API for courier management. This suite covers two core endpoints:

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/v1/courier` | POST | Create a new courier account |
| `/api/v1/courier/login` | POST | Authenticate and retrieve courier ID |
| `/api/v1/courier/:id` | DELETE | Remove a courier by ID |

---

## Test strategy

Tests are organized into three categories using pytest markers:

- **smoke** — happy-path validation; run first to confirm the server is healthy
- **regression** — boundary value analysis (BVA) on all required and optional fields
- **negative** — invalid inputs, missing fields, duplicate accounts, malformed IDs

Every test asserts on three things:
1. HTTP status code
2. Response body structure (JSON schema validation via `jsonschema`)
3. Response time (must be under 2 seconds)

---

## Bugs discovered

During test execution against the live Urban Scooter server, **23 real defects** were identified and filed in Jira (tickets P9-15 through P9-36).

Key findings:

| Jira | Severity | Description |
|---|---|---|
| P9-15 | Critical | DELETE returns 404 for a courier confirmed to exist via login |
| P9-16 | High | DELETE with alphabetic ID returns 500 with raw PostgreSQL error |
| P9-17 | High | DELETE with decimal ID exposes raw DB error (500) |
| P9-18 | High | DELETE with integer overflow ID exposes raw DB error (500) |
| P9-19 to P9-36 | Medium | POST accepts invalid field values — no server-side validation on login, password, or firstName |

The mock server in `mock_server/app.py` implements the **correct** behaviour as per requirements, so CI tests run green and document what the fixed API should return.

---

## Project structure

```
urban-scooter-api-tests/
├── .github/
│   └── workflows/
│       └── test.yml          # GitHub Actions CI pipeline
├── config/
│   └── settings.py           # Base URL, endpoint constants, thresholds
├── mock_server/
│   └── app.py                # Flask mock API — used in CI
├── schemas/
│   └── courier.py            # JSON schema definitions for all responses
├── tests/
│   ├── test_create_courier.py
│   └── test_delete_courier.py
├── utils/
│   └── api_client.py         # CourierAPI wrapper class
├── conftest.py               # Shared pytest fixtures
├── pytest.ini                # Markers, report config, test paths
└── requirements.txt
```

---

## Run locally

**Prerequisites:** Python 3.11+, pip

```bash
# Clone and install
git clone https://github.com/mgcg4725-maker/urban-scooter-api-tests.git
cd urban-scooter-api-tests
pip install -r requirements.txt

# Option 1 — Run against the live TripleTen server
export BASE_URL=https://your-server.containerhub.tripleten-services.com
pytest

# Option 2 — Run against the local mock server
python mock_server/app.py &
export BASE_URL=http://localhost:5000
pytest

# Run only smoke tests
pytest -m smoke

# Run only negative tests
pytest -m negative

# Generate HTML report (saved to reports/test-report.html)
pytest --html=reports/test-report.html --self-contained-html
```

---

## CI pipeline

Every push to `main` triggers the GitHub Actions workflow which:

1. Spins up the Flask mock server
2. Runs smoke tests first — fails fast if core behaviour is broken
3. Runs the full suite
4. Uploads the HTML test report as a downloadable artifact

---

## Tech stack

| Tool | Purpose |
|---|---|
| Python 3.11 | Primary language |
| pytest | Test runner and assertion framework |
| requests | HTTP client |
| jsonschema | Response body schema validation |
| Flask | Mock API server (CI only) |
| GitHub Actions | CI/CD pipeline |
| Jira | Bug tracking (michael-garcia.atlassian.net) |
| Postman | Manual API exploration and initial verification |

---

## Author

**Michael Garcia** — QA Engineer, Backend API Automation  
[LinkedIn](https://linkedin.com/in/michael-garcia03) · [GitHub](https://github.com/mgcg4725-maker)
