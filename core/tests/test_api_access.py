"""Who may call the local API: only a caller that has the secret of this launch."""

import pytest
from conftest import SECRET, open_api
from fastapi.testclient import TestClient

from trace_telemetry.api import create_app


@pytest.fixture
def stranger(data_dir) -> TestClient:
    """A caller on the same machine that was never given the secret."""
    return TestClient(create_app(data_dir=data_dir, secret=SECRET))


def test_a_request_without_the_secret_is_rejected(stranger, data_dir, car_fixture):
    assert stranger.get("/logs").status_code == 401

    response = stranger.post("/logs/import", json={"path": str(car_fixture.path)})

    assert response.status_code == 401
    assert open_api(data_dir).get("/logs").json() == []


def test_a_request_with_the_wrong_secret_is_rejected(stranger):
    response = stranger.get("/logs", headers={"Authorization": "Bearer not-the-secret"})

    assert response.status_code == 401


@pytest.mark.parametrize("path", ["/", "/docs", "/openapi.json", "/logs/any-id", "/no-such-path"])
def test_nothing_at_all_is_served_without_the_secret(stranger, path):
    assert stranger.get(path).status_code == 401


UI_ORIGIN = "http://localhost:5173"


@pytest.fixture
def browser(data_dir) -> TestClient:
    """A browser, which sends no secret unless the page it shows adds one."""
    return TestClient(create_app(data_dir=data_dir, secret=SECRET, ui_origin=UI_ORIGIN))


def preflight(browser: TestClient, origin: str):
    """What a browser asks, without the secret, before a page may send the real request."""
    return browser.options(
        "/logs",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )


def test_the_user_interface_may_call_the_api_from_its_own_origin(browser):
    asked = preflight(browser, UI_ORIGIN)

    assert asked.status_code == 200
    assert asked.headers["access-control-allow-origin"] == UI_ORIGIN
    assert "authorization" in asked.headers["access-control-allow-headers"].lower()

    response = browser.get(
        "/logs", headers={"Origin": UI_ORIGIN, "Authorization": f"Bearer {SECRET}"}
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == UI_ORIGIN


def test_a_page_from_any_other_origin_is_not_let_in(browser):
    asked = preflight(browser, "https://example.com")

    assert "access-control-allow-origin" not in asked.headers
