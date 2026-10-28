
import pytest
import database

from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Give each test its own temporary database.
    test_db = tmp_path / "test_tasks.db"
    monkeypatch.setattr(database, "DATABASE_NAME", str(test_db))

    with TestClient(app) as test_client:
        yield test_client


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_and_list_tasks(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Learn pytest",
            "description": "Automate API testing",
        },
    )

    assert response.status_code == 201
    task = response.json()
    assert task["id"] > 0
    assert task["title"] == "Learn pytest"

    list_response = client.get("/tasks")

    assert list_response.status_code == 200
    assert task in list_response.json()


def test_get_missing_task_returns_404(client):
    response = client.get("/tasks/9999")

    assert response.status_code == 404


def test_put_replaces_task(client):
    created = client.post(
        "/tasks",
        json={"title": "Old title", "description": "Old description"},
    ).json()

    response = client.put(
        f"/tasks/{created['id']}",
        json={"title": "New title", "description": "New description"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "New title"
    assert response.json()["description"] == "New description"


def test_patch_changes_only_supplied_field(client):
    created = client.post(
        "/tasks",
        json={"title": "Original", "description": "Keep this"},
    ).json()

    response = client.patch(
        f"/tasks/{created['id']}",
        json={"title": "Updated"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated"
    assert response.json()["description"] == "Keep this"


def test_delete_task(client):
    created = client.post(
        "/tasks",
        json={"title": "Delete me", "description": ""},
    ).json()
    task_id = created["id"]

    delete_response = client.delete(f"/tasks/{task_id}")

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404


def test_invalid_create_returns_422(client):
    response = client.post(
        "/tasks",
        json={"description": "Missing required title"},
    )

    assert response.status_code == 422
