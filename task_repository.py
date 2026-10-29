
from database import get_connection


def create_task(title: str, description: str) -> dict:
    connection = get_connection()

    try:
        cursor = connection.execute(
            "INSERT INTO tasks (title, description) VALUES (?, ?)",
            (title, description),
        )
        connection.commit()

        row = connection.execute(
            "SELECT id, title, description FROM tasks WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()

        return dict(row)
    finally:
        connection.close()


def get_tasks() -> list[dict]:
    connection = get_connection()

    try:
        rows = connection.execute(
            "SELECT id, title, description FROM tasks ORDER BY id"
        ).fetchall()

        return [dict(row) for row in rows]
    finally:
        connection.close()


def get_tasks(skip: int = 0, limit: int = 10) -> list[dict]:
    connection = get_connection()
    try:
        rows = connection.execute(
            """
            SELECT id, title, description
            FROM tasks
            ORDER BY id
            LIMIT ? OFFSET ?
            """,
            (limit, skip),
        ).fetchall()

        return [dict(row) for row in rows]
    finally:
        connection.close()

def replace_task(task_id: int, title: str, description: str) -> dict | None:
    connection = get_connection()

    try:
        cursor = connection.execute(
            "UPDATE tasks SET title = ?, description = ? WHERE id = ?",
            (title, description, task_id),
        )

        if cursor.rowcount == 0:
            return None

        connection.commit()

        row = connection.execute(
            "SELECT id, title, description FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        return dict(row)
    finally:
        connection.close()


def update_task(task_id: int, changes: dict) -> dict | None:
    allowed_fields = {"title", "description"}

    if not changes or not set(changes).issubset(allowed_fields):
        raise ValueError("Invalid task update fields")

    connection = get_connection()

    try:
        assignments = ", ".join(
            f"{field} = ?" for field in changes
        )
        values = list(changes.values()) + [task_id]

        cursor = connection.execute(
            f"UPDATE tasks SET {assignments} WHERE id = ?",
            values,
        )

        if cursor.rowcount == 0:
            return None

        connection.commit()

        row = connection.execute(
            "SELECT id, title, description FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        return dict(row)
    finally:
        connection.close()

def get_task(task_id: int) -> dict | None:
    connection = get_connection()
    try:
        row = connection.execute(
            "SELECT id, title, description FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        return dict(row) if row is not None else None
    finally:
        connection.close()

def delete_task(task_id: int) -> bool:
    connection = get_connection()

    try:
        cursor = connection.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,),
        )

        if cursor.rowcount == 0:
            return False

        connection.commit()
        return True
    finally:
        connection.close()

