from fastapi import FastAPI, HTTPException, Response, status
from fastapi import Query, Path
from contextlib import asynccontextmanager
from database import create_table, get_connection
from schemas import TaskCreate, TaskUpdate,TaskRead
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

@app.post("/tasks", status_code=status.HTTP_201_CREATED,
    response_model=TaskRead,)
def create_task(task: TaskCreate):
    return task_repository.create_task(
        title=task.title,
        description=task.description,
    )


@app.get(
    "/tasks/{task_id}",
    response_model=TaskRead,
    responses={404: {"description": "Task not found"}},
)
def get_task(task_id: int = Path(ge=1)):
    task = task_repository.get_task(task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task

@app.get("/tasks",response_model=list[TaskRead])
def list_tasks(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
):
    return task_repository.get_tasks(
        skip=skip,
        limit=limit,
    )

@app.put("/tasks/{task_id}", response_model=TaskRead,responses={404: {"description": "Task not found"}})
def replace_task(
    *,
    task_id: int = Path(ge=1),
    updated_task: TaskCreate,
):
    task = task_repository.replace_task(
        task_id=task_id,
        title=updated_task.title,
        description=updated_task.description,
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task

@app.patch("/tasks/{task_id}", response_model=TaskRead,responses={404: {"description": "Task not found"}})
def update_task(*,task_id: int = Path(ge=1), updates: TaskUpdate):
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
    responses={404: {"description": "Task not found"}}
)
def delete_task(task_id: int = Path(ge=1)):
    deleted = task_repository.delete_task(task_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
