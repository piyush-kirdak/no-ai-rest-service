
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel

from database import create_table, get_connection

app = FastAPI(title="No-AI REST Service")


class TaskCreate(BaseModel):
    title: str
    description: str = ""


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


# Create the database table when the app starts.
@app.on_event("startup")
def startup():
    create_table()


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    connection = get_connection()

    try:
        cursor = connection.execute(
            "INSERT INTO tasks (title, description) VALUES (?, ?)",
            (task.title, task.description),
        )
        connection.commit()

        new_task = connection.execute(
            "SELECT id, title, description FROM tasks WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()

        return dict(new_task)
    finally:
        connection.close()


@app.get("/tasks")
def get_tasks():
    connection = get_connection()

    try:
        rows = connection.execute(
            "SELECT id, title, description FROM tasks ORDER BY id"
        ).fetchall()

        return [dict(row) for row in rows]
    finally:
        connection.close()


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    connection = get_connection()

    try:
        row = connection.execute(
            "SELECT id, title, description FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="Task not found")

        return dict(row)
    finally:
        connection.close()


@app.put("/tasks/{task_id}")
def replace_task(task_id: int, updated_task: TaskCreate):
    connection = get_connection()

    try:
        cursor = connection.execute(
            "UPDATE tasks SET title = ?, description = ? WHERE id = ?",
            (updated_task.title, updated_task.description, task_id),
        )

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found")

        connection.commit()

        row = connection.execute(
            "SELECT id, title, description FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        return dict(row)
    finally:
        connection.close()


@app.patch("/tasks/{task_id}")
def update_task(task_id: int, updates: TaskUpdate):
    changes = updates.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=422,
            detail="Provide at least one field to update",
        )

    for field, value in changes.items():
        if value is None:
            raise HTTPException(
                status_code=422,
                detail=f"{field} cannot be null",
            )

    allowed_fields = {"title", "description"}
    if not set(changes).issubset(allowed_fields):
        raise HTTPException(status_code=422, detail="Invalid field")

    connection = get_connection()

    try:
        exists = connection.execute(
            "SELECT id FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()

        if exists is None:
            raise HTTPException(status_code=404, detail="Task not found")

        for field, value in changes.items():
            connection.execute(
                f"UPDATE tasks SET {field} = ? WHERE id = ?",
                (value, task_id),
            )

        connection.commit()

        row = connection.execute(
            "SELECT id, title, description FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        return dict(row)
    finally:
        connection.close()


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    connection = get_connection()

    try:
        cursor = connection.execute(
            "DELETE FROM tasks WHERE id = ?", (task_id,)
        )

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found")

        connection.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    finally:
        connection.close()
