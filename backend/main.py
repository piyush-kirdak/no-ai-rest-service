from fastapi import FastAPI, HTTPException, Response, status, Depends
from fastapi import Query, Path
from contextlib import asynccontextmanager
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.database import create_table, get_connection
from backend.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskRead,
    UserLogin,
    TokenResponse,
    UserCreate,
    UserResponse,
)

from backend import task_repository, user_repository
from backend.security import create_access_token, verify_access_token

from pwdlib import PasswordHash
# password hasher initialize
password_hash = PasswordHash.recommended()
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_table()
    yield


app = FastAPI(
    title="No-AI REST Service",
    lifespan=lifespan,
)

bearer_scheme = HTTPBearer()
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    token = credentials.credentials

    try:
        user_id = verify_access_token(token)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = user_repository.get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post(
    "/auth/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
)
def register_user(user: UserCreate):

    hashed_password = password_hash.hash(user.password)

    try:
        new_user = user_repository.create_user(
            name=user.name,
            email=user.email,
            hashed_password=hashed_password,
        )

        return new_user

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )

@app.post("/auth/login", response_model=TokenResponse)
def login_user(credentials: UserLogin):

    user = user_repository.get_user_by_email(credentials.email)

    if user is None or not password_hash.verify(
        credentials.password,
        user["hashed_password"],
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(user["id"])

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
@app.get("/users/me", response_model=UserResponse)
def read_current_user(
    current_user: dict = Depends(get_current_user),
):
    return current_user

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
