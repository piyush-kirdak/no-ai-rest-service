# No-AI REST Service

A RESTful Task Management API built with Python, FastAPI, Pydantic, and SQLite. The project demonstrates CRUD operations, request validation, persistent storage, pagination, structured repository logic, and automated testing.

## Features

- **Task CRUD operations** — Create, retrieve, list, replace, update, and delete tasks.
- **SQLite persistence** — Store tasks in a local database.
- **Input validation** — Validate request data using Pydantic schemas.
- **Pagination** — Retrieve tasks using `skip` and `limit` query parameters.
- **Error handling** — Return appropriate HTTP errors for missing tasks and invalid updates.
- **Health check** — Check whether the API is responding.
- **Repository layer** — Separate task data operations from API endpoint logic.
- **Automated tests** — Test API behavior using Pytest.
- **Interactive API documentation** — Explore and test endpoints through FastAPI's Swagger UI.

## Tech Stack

- Python
- FastAPI
- Pydantic
- SQLite
- Pytest
- Uvicorn

## Project Structure

```text
no-ai-rest-service/
├── main.py              # FastAPI application and endpoints
├── database.py          # Database connection and table setup
├── schemas.py            # Pydantic request and response schemas
├── task_repository.py    # Task CRUD and database operations
├── test_main.py          # Automated API tests
├── tasks.db              # Local SQLite database (generated/used locally)
├── .env                  # Local environment configuration
├── .gitignore            # Git ignore rules
└── README.md             # Project documentation
```

## Getting Started

### 1. Prerequisites

- Python 3.10 or newer
- pip

### 2. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd no-ai-rest-service
```

Replace `<YOUR_GITHUB_REPOSITORY_URL>` with your actual repository URL.

### 3. Create a Virtual Environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks environment activation, use the appropriate execution policy for your machine or run the virtual environment's Python executable directly.

### 4. Install Dependencies

Install the packages used by the project:

```bash
python -m pip install fastapi uvicorn pydantic pytest httpx
```

If the project already has a dependency file, prefer installing from that file instead.

### 5. Run the API

```bash
uvicorn main:app --reload
```

The API will normally be available at:

- API base URL: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

The database table is initialized when the application starts.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check API health |
| POST | `/tasks` | Create a task |
| GET | `/tasks` | List tasks |
| GET | `/tasks/{task_id}` | Get a task by ID |
| PUT | `/tasks/{task_id}` | Replace a task |
| PATCH | `/tasks/{task_id}` | Update selected task fields |
| DELETE | `/tasks/{task_id}` | Delete a task |

### Health Check

**Request**

```http
GET /health
```

**Response**

```json
{
  "status": "healthy"
}
```

### Create a Task

**Request**

```http
POST /tasks
Content-Type: application/json
```

```json
{
  "title": "Learn FastAPI",
  "description": "Build a REST API project"
}
```

A successful request returns `201 Created` and the created task, including its generated ID.

### List Tasks

```http
GET /tasks?skip=0&limit=10
```

- `skip`: Number of tasks to skip; defaults to `0`.
- `limit`: Maximum number of tasks to return; defaults to `10`, with a maximum of `100`.

### Get a Task

```http
GET /tasks/1
```

Returns the task if it exists; otherwise, returns `404 Not Found`.

### Replace a Task

```http
PUT /tasks/1
Content-Type: application/json
```

```json
{
  "title": "Learn FastAPI thoroughly",
  "description": "Complete the REST API project"
}
```

Replaces the task's title and description.

### Partially Update a Task

```http
PATCH /tasks/1
Content-Type: application/json
```

```json
{
  "description": "Practice API testing"
}
```

Only the supplied fields are updated. At least one field must be provided.

### Delete a Task

```http
DELETE /tasks/1
```

A successful deletion returns `204 No Content`. If the task does not exist, the API returns `404 Not Found`.

## Validation and Error Handling

- Task titles must contain between 1 and 100 characters.
- Task IDs must be greater than or equal to `1`.
- The list endpoint limits page size to between `1` and `100`.
- Missing tasks return `404 Not Found`.
- Invalid request data is rejected by FastAPI/Pydantic.
- An empty PATCH request or an update containing a null field is rejected with `422 Unprocessable Entity`.

## Running Tests

Run the test suite from the project root:

```bash
pytest -v
```

To run a specific test file:

```bash
pytest test_main.py -v
```

## Database

The project uses SQLite for persistent local storage. Database connection and table initialization are handled by `database.py`, while task-related database operations are managed by `task_repository.py`.

## Future Improvements

Potential next steps include:

- Add authentication and authorization.
- Add structured logging.
- Add database migrations.
- Add Docker support.
- Add CI checks through GitHub Actions.
- Improve test coverage and API performance.

## License

No license has been specified yet. Add a `LICENSE` file if you intend to distribute the project under an open-source license.
