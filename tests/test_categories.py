"""Tests for category endpoints and app-level behavior."""

def test_category_crud(client):
    created = client.post(
        "/categories", json={"name": "work", "description": "job stuff"}
    )
    assert created.status_code == 201
    category = created.json()
    assert category["name"] == "work"

    got = client.get(f"/categories/{category['id']}")
    assert got.status_code == 200

    updated = client.patch(
        f"/categories/{category['id']}", json={"name": "career"}
    )
    assert updated.json()["name"] == "career"

    assert client.delete(f"/categories/{category['id']}").status_code == 200
    assert client.get(f"/categories/{category['id']}").status_code == 404


def test_category_names_must_be_unique(client):
    client.post("/categories", json={"name": "dup"})
    response = client.post("/categories", json={"name": "dup"})
    assert response.status_code == 422


def test_category_requires_name(client):
    assert client.post("/categories", json={"description": "x"}).status_code == 422


def test_categories_list_paginated(client):
    for i in range(3):
        client.post("/categories", json={"name": f"cat-{i}"})
    body = client.get("/categories").json()
    assert body["total"] == 3
    assert len(body["items"]) == 3
    assert set(body) == {"items", "total", "page", "page_size", "total_pages"}


def test_openapi_docs_available(client):
    assert client.get("/docs").status_code == 200
    openapi = client.get("/openapi.json").json()
    assert "/tasks" in openapi["paths"]
    assert "/categories" in openapi["paths"]
