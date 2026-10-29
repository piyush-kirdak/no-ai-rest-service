
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

def test_create_task_rejects_empty_title(client):
    response = client.post(
        "/tasks",
        json={"title": ""}
    )

    assert response.status_code == 422


def test_create_task_rejects_long_title(client):
    response = client.post(
        "/tasks",
        json={"title": "A" * 101}
    )

    assert response.status_code == 422


def test_update_task_rejects_empty_title(client):
    response = client.patch(
        "/tasks/1",
        json={"title": ""}
    )

    assert response.status_code == 422

def test_create_task_response_has_expected_fields(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Learn FastAPI",
            "description": "Practice response models",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert data["title"] == "Learn FastAPI"
    assert data["description"] == "Practice response models"

def test_get_task_response_has_expected_fields(client):
    create_response = client.post(
        "/tasks",
        json={
            "title": "Original title",
            "description": "Test description",
        },
    )
    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Original title"
    assert data["description"] == "Test description"


def test_put_task_response_has_expected_fields(client):
    create_response = client.post(
        "/tasks",
        json={"title": "Old title", "description": "Old description"},
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    response = client.put(
        f"/tasks/{task_id}",
        json={"title": "New title", "description": "New description"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "New title"
    assert data["description"] == "New description"


def test_patch_task_response_has_expected_fields(client):
    create_response = client.post(
        "/tasks",
        json={"title": "Old title", "description": "Keep this"},
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={"title": "Updated title"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Updated title"
    assert data["description"] == "Keep this"


def test_create_task_without_description(client):
    response = client.post(
        "/tasks",
        json={"title": "Task without description"},
    )

    assert response.status_code == 201
    assert response.json()["description"] == ""
def test_tasks_list_is_empty_for_new_database(client):
    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == []

def test_create_task_does_not_leak_to_other_tests(client):
    response = client.post(
        "/tasks",
        json={"title": "Isolation test"},
    )

    assert response.status_code == 201


def test_new_client_has_no_previous_tasks(client):
    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == []

def test_delete_missing_task_returns_404(client):
    response = client.delete("/tasks/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}

def test_openapi_schema_contains_task_endpoints(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200

    schema = response.json()
    paths = schema["paths"]

    assert "/tasks" in paths
    assert "/tasks/{task_id}" in paths

    assert "get" in paths["/tasks"]
    assert "post" in paths["/tasks"]

    assert "get" in paths["/tasks/{task_id}"]
    assert "put" in paths["/tasks/{task_id}"]
    assert "patch" in paths["/tasks/{task_id}"]
    assert "delete" in paths["/tasks/{task_id}"]

def test_openapi_documents_expected_status_codes(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200

    paths = response.json()["paths"]

    assert "201" in paths["/tasks"]["post"]["responses"]
    assert "200" in paths["/tasks"]["get"]["responses"]

    task_path = paths["/tasks/{task_id}"]

    assert "200" in task_path["get"]["responses"]
    assert "404" in task_path["get"]["responses"]
    assert "204" in task_path["delete"]["responses"]
    assert "404" in task_path["delete"]["responses"]
