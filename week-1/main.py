from fastapi import FastAPI
from fastapi import HTTPException, status
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