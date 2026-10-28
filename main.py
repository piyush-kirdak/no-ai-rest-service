from fastapi import FastAPI, HTTPException, Response, status
from contextlib import asynccontextmanager
from database import create_table, get_connection
from schemas import TaskCreate, TaskUpdate
import task_repository
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_table()
    yield


app = FastAPI(
    title="No-AI REST Service",
    lifespan=lifespan,
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    return task_repository.create_task(
        title=task.title,
        description=task.description,
    )
@app.get("/tasks")
def get_tasks():
    return task_repository.get_tasks()

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = task_repository.get_task(task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task


@app.put("/tasks/{task_id}")
def replace_task(task_id: int, updated_task: TaskCreate):
    task = task_repository.replace_task(
        task_id=task_id,
        title=updated_task.title,
        description=updated_task.description,
    )

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task



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

    task = task_repository.update_task(task_id, changes)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task

@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(task_id: int):
    deleted = task_repository.delete_task(task_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
