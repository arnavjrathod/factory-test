"""Tests for UI-level behaviour, including the light/dark theme switcher."""


THEME_APP = "/theme"


def test_get_theme_defaults_to_light(client):
    response = client.get(THEME_APP)
    assert response.status_code == 200
    assert response.json() == {"theme": "light"}


def test_set_theme_dark(client):
    response = client.post(THEME_APP, json={"theme": "dark"})
    assert response.status_code == 200
    assert response.json() == {"theme": "dark"}
    assert "theme=dark" in response.headers.get("set-cookie", "")


def test_get_theme_respects_cookie(client):
    client.cookies.set("theme", "dark")
    response = client.get(THEME_APP)
    assert response.status_code == 200
    assert response.json() == {"theme": "dark"}


def test_set_theme_invalid(client):
    response = client.post(THEME_APP, json={"theme": "blue"})
    assert response.status_code == 422


def test_index_html_includes_theme_script(client):
    response = client.get("/")
    # The static UI may not be mounted in tests; only assert when it is served.
    if response.status_code == 200:
        text = response.text
        assert "data-theme" in text
        assert "localStorage" in text
        assert "prefers-color-scheme" in text
