
import sqlite3
from backend.database import get_connection


def create_user(
    name: str,
    email: str,
    hashed_password: str,
) -> dict:
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO users (name, email, hashed_password)
            VALUES (?, ?, ?)
            """,
            (name, email, hashed_password),
        )

        connection.commit()

        row = connection.execute(
            """
            SELECT id, name, email
            FROM users
            WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()

        return dict(row)

    except sqlite3.IntegrityError as error:
        raise ValueError("Email already registered") from error

    finally:
        connection.close()


def get_user_by_email(email: str) -> dict | None:
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT id, name, email, hashed_password
            FROM users
            WHERE email = ?
            """,
            (email,),
        ).fetchone()

        return dict(row) if row is not None else None

    finally:
        connection.close()


def get_user_by_id(user_id: int) -> dict | None:
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT id, name, email
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()

        return dict(row) if row is not None else None

    finally:
        connection.close()