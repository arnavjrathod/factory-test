"""Tests for task endpoints: user stories US-01..US-08 and FR-01..FR-07."""

import datetime as dt

TODO_APP = "/tasks"


def _create(client, **overrides):
    payload = {"title": "Test task"}
    payload.update(overrides)
    response = client.post(TODO_APP, json=payload)
    assert response.status_code == 201, response.text
    return response.json()


# ---- US-01 / FR-01: creation ----

def test_create_task_minimal(client):
    task = _create(client)
    assert task["title"] == "Test task"
    assert task["status"] == "todo"
    assert task["priority"] == "medium"
    assert task["description"] is None
    assert task["due_date"] is None
    assert task["category_id"] is None
    assert task["overdue"] is False


def test_create_task_requires_title(client):
    response = client.post(TODO_APP, json={"description": "no title"})
    assert response.status_code == 422
    assert "detail" in response.json()


def test_create_task_with_all_fields(client):
    task = _create(
        client,
        title="Full",
        description="desc",
        status="in_progress",
        priority="high",
        due_date="2030-01-15",
    )
    assert task["status"] == "in_progress"
    assert task["priority"] == "high"
    assert task["due_date"] == "2030-01-15"
    assert task["description"] == "desc"


def test_create_task_invalid_enum(client):
    response = client.post(TODO_APP, json={"title": "x", "status": "bogus"})
    assert response.status_code == 422
    response = client.post(TODO_APP, json={"title": "x", "priority": "urgent"})
    assert response.status_code == 422


def test_create_task_malformed_date(client):
    response = client.post(TODO_APP, json={"title": "x", "due_date": "not-a-date"})
    assert response.status_code == 422


# ---- US-03 / FR-02: status transitions ----

def test_status_transitions_free(client):
    task = _create(client)
    for status in ("in_progress", "done", "todo", "done"):
        response = client.patch(f"{TODO_APP}/{task['id']}", json={"status": status})
        assert response.status_code == 200
        assert response.json()["status"] == status


# ---- US-04: edit ----

def test_update_task_fields(client):
    task = _create(client, title="Old")
    response = client.patch(
        f"{TODO_APP}/{task['id']}",
        json={"title": "New", "description": "updated", "priority": "low"},
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["title"] == "New"
    assert updated["description"] == "updated"
    assert updated["priority"] == "low"


def test_update_empty_body_is_noop(client):
    task = _create(client, title="Keep")
    response = client.patch(f"{TODO_APP}/{task['id']}", json={})
    assert response.status_code == 200
    assert response.json()["title"] == "Keep"


# ---- US-05: delete ----

def test_delete_task(client):
    task = _create(client)
    assert client.delete(f"{TODO_APP}/{task['id']}").status_code == 200
    assert client.get(f"{TODO_APP}/{task['id']}").status_code == 404
    assert client.delete(f"{TODO_APP}/{task['id']}").status_code == 404


# ---- FR-03: overdue flag ----

def test_overdue_flag(client):
    past = (dt.date.today() - dt.timedelta(days=1)).isoformat()
    future = (dt.date.today() + dt.timedelta(days=7)).isoformat()

    overdue_task = _create(client, title="overdue", due_date=past)
    future_task = _create(client, title="future", due_date=future)
    overdue_done = _create(client, title="done overdue", due_date=past)

    client.patch(f"{TODO_APP}/{overdue_done['id']}", json={"status": "done"})

    listed = client.get(TODO_APP).json()["items"]
    flags = {t["id"]: t["overdue"] for t in listed}
    assert flags[overdue_task["id"]] is True
    assert flags[future_task["id"]] is False
    assert flags[overdue_done["id"]] is False


# ---- US-06 / FR-05: filtering & sorting ----

def test_filter_by_status(client):
    a = _create(client, title="A")
    _create(client, title="B")
    client.patch(f"{TODO_APP}/{a['id']}", json={"status": "done"})

    items = client.get(TODO_APP, params={"status": "done"}).json()["items"]
    assert [t["title"] for t in items] == ["A"]


def test_filter_by_priority(client):
    _create(client, title="Low", priority="low")
    _create(client, title="High", priority="high")

    items = client.get(TODO_APP, params={"priority": "high"}).json()["items"]
    assert [t["title"] for t in items] == ["High"]


def test_filter_by_category(client):
    cat = client.post("/categories", json={"name": "work"}).json()
    _create(client, title="In cat", category_id=cat["id"])
    _create(client, title="No cat")

    items = client.get(TODO_APP, params={"category_id": cat["id"]}).json()["items"]
    assert [t["title"] for t in items] == ["In cat"]


def test_combined_filters(client):
    cat = client.post("/categories", json={"name": "home"}).json()
    _create(client, title="Match", priority="high", category_id=cat["id"])
    _create(client, title="Wrong prio", priority="low", category_id=cat["id"])
    _create(client, title="No cat", priority="high")

    items = client.get(
        TODO_APP, params={"priority": "high", "category_id": cat["id"]}
    ).json()["items"]
    assert [t["title"] for t in items] == ["Match"]


def test_sort_by_due_date(client):
    _create(client, title="C", due_date="2030-03-01")
    _create(client, title="A", due_date="2030-01-01")
    _create(client, title="NoDate")
    _create(client, title="B", due_date="2030-02-01")

    asc = [t["title"] for t in
           client.get(TODO_APP, params={"sort": "due_date", "order": "asc"}).json()["items"]]
    assert asc == ["A", "B", "C", "NoDate"]

    desc = [t["title"] for t in
            client.get(TODO_APP, params={"sort": "due_date", "order": "desc"}).json()["items"]]
    assert desc == ["C", "B", "A", "NoDate"]


def test_sort_by_priority(client):
    _create(client, title="M", priority="medium")
    _create(client, title="H", priority="high")
    _create(client, title="L", priority="low")

    asc = [t["title"] for t in
           client.get(TODO_APP, params={"sort": "priority", "order": "asc"}).json()["items"]]
    assert asc == ["H", "M", "L"]  # high first

    desc = [t["title"] for t in
            client.get(TODO_APP, params={"sort": "priority", "order": "desc"}).json()["items"]]
    assert desc == ["L", "M", "H"]


def test_invalid_sort_value(client):
    assert client.get(TODO_APP, params={"sort": "title"}).status_code == 422


# ---- US-07 / FR-04: categories ----

def test_assign_category_on_create_and_update(client):
    cat = client.post("/categories", json={"name": "errands"}).json()
    task = _create(client, title="T", category_id=cat["id"])
    assert task["category_id"] == cat["id"]

    cat2 = client.post("/categories", json={"name": "other"}).json()
    response = client.patch(f"{TODO_APP}/{task['id']}", json={"category_id": cat2["id"]})
    assert response.json()["category_id"] == cat2["id"]


def test_create_task_with_unknown_category(client):
    response = client.post(TODO_APP, json={"title": "T", "category_id": 9999})
    assert response.status_code == 422


def test_category_deletion_keeps_tasks(client):
    cat = client.post("/categories", json={"name": "temp"}).json()
    task = _create(client, title="Survivor", category_id=cat["id"])

    assert client.delete(f"/categories/{cat['id']}").status_code == 200
    task_after = client.get(f"{TODO_APP}/{task['id']}").json()
    assert task_after["category_id"] is None


# ---- US-08: view tasks sorted ----

def test_list_endpoint_paginated_shape(client):
    response = client.get(TODO_APP)
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"items", "total", "page", "page_size", "total_pages"}


# ---- FR-07: pagination ----

def test_pagination_defaults_and_limits(client):
    for i in range(25):
        _create(client, title=f"task-{i:02d}")

    body = client.get(TODO_APP).json()
    assert body["total"] == 25
    assert body["page"] == 1
    assert body["page_size"] == 20
    assert body["total_pages"] == 2
    assert len(body["items"]) == 20

    page2 = client.get(TODO_APP, params={"page": 2}).json()
    assert len(page2["items"]) == 5

    capped = client.get(TODO_APP, params={"page_size": 500})
    assert capped.status_code == 422

    small = client.get(TODO_APP, params={"page_size": 5, "page": 3}).json()
    assert [t["title"] for t in small["items"]] == ["task-10", "task-11",
                                                    "task-12", "task-13",
                                                    "task-14"]


# ---- Error handling ----

def test_structured_error_on_missing_task(client):
    response = client.get(f"{TODO_APP}/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}
