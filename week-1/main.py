from fastapi import FastAPI
from fastapi import HTTPException, status
from pydantic import BaseModel
app = FastAPI()

tasks = [
    {"id": 1, "title": "Task 1", "done": "True"},
    {"id": 2, "title": "Task 2", "done": "False"},
    {"id": 3, "title": "Task 3", "done": "False"}
]

@app.get("/")
async def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/tasks")
async def get_tasks():
    return tasks

@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    task = next((task for task in tasks if task["id"] == task_id), None)
    if task:
        return task
    raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )

class Tasktitle(BaseModel):
    title: str

@app.post("/createTasks", status_code=status.HTTP_201_CREATED)
async def create_task(task: Tasktitle):
    if not task.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task title is required"
        )
    
    new_task = {
        "id": len(tasks) + 1,
        "title": task.title,
        "done": False
    }
    tasks.append(new_task)
    return new_task


class updateTask(BaseModel):
    title: str
    done: bool

@app.put("/tasks/{task_id}")
async def update_task(task_id: int, updated_task: updateTask):

    if not updated_task.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task title is required"
        )
    task = next((task for task in tasks if task["id"] == task_id), None)
    if task:
        task["title"] = updated_task.title
        task["done"] = updated_task.done
        return task
    raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )

@app.delete("/tasks/{task_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int):
    task = next((task for task in tasks if task["id"] == task_id), None)
    if task:
        tasks.remove(task)
        return {"message": f"Task with ID {task_id} deleted successfully"}
    raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
