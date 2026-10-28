from fastapi import FastAPI, HTTPException, Response, status
from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI(title="No-AI REST Service")


# 1. Define the structure of incoming task data
class TaskCreate(BaseModel):
    title: str
    description: str = ""
# 2.Updating feature:
class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


# 2. Temporary storage for tasks
tasks = []
next_task_id = 1


# 3. Health endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}


# 4. Create a new task
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    global next_task_id

    new_task = {
        "id": next_task_id,
        "title": task.title,
        "description": task.description,
    }

    tasks.append(new_task)
    next_task_id += 1

    return new_task


# Get all tasks
@app.get("/tasks")
def get_tasks():
    return tasks


# Get one task by ID
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task

    raise HTTPException(
        status_code=404,
        detail="Task not found",
    )


@app.put("/tasks/{task_id}")
def replace_task(task_id: int, updated_task: TaskCreate):
    for task in tasks:
        if task["id"] == task_id:
            task["title"] = updated_task.title
            task["description"] = updated_task.description
            return task

    raise HTTPException(
        status_code=404,
        detail="Task not found",
    )


@app.patch("/tasks/{task_id}")
def update_task(task_id: int, updates: TaskUpdate):
    for task in tasks:
        if task["id"] == task_id:
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
                task[field] = value

            return task

    raise HTTPException(
        status_code=404,
        detail="Task not found",
    )


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(task_id: int):
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(index)
            return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(
        status_code=404,
        detail="Task not found",
    )

