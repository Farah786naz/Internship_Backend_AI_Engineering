from fastapi import FastAPI
from fastapi import HTTPException, status , Depends
from pydantic import BaseModel
from contextlib import asynccontextmanager
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# This creates a local file named tasks.db in this folder
DATABASE_URL = "sqlite:///./tasks.db"
app = FastAPI()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
tasks = []

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    done = Column(Boolean, default=False)


# --- DATABASE SESSION DEPENDENCY ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- LIFESPAN (STARTUP LOGIC) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs ON STARTUP
    db = SessionLocal()
    try:
        # 1. Count the rows in the tasks table
        task_count = db.query(Task).count()
        print(f"Current task count on startup: {task_count}")

        # 2. Only insert if the table is completely empty (0 rows)
        if task_count == 0:
            print("Table is empty! Seeding 3 example tasks...")
            example_tasks = [
                Task(title="Buy groceries", description="Milk, eggs, and bread", done=False),
                Task(title="Clean the room", description="Vacuum and dust the shelves", done=True),
                Task(title="Learn FastAPI", description="Finish the database checkpoint", done=False)
            ]
            db.add_all(example_tasks)
            db.commit() # Save permanently to tasks.db
            print("Seeding complete.")
        else:
            print("Table already has data. Skipping seed.")
    finally:
        db.close()
        
    yield # The application runs here
    
    # Any code written here runs ON SHUTDOWN

# --- INITIALIZE FASTAPI WITH LIFESPAN ---
app = FastAPI(lifespan=lifespan)
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
async def get_tasks( db : Session = Depends(get_db)):
    return db.query(Task).all()

@app.get("/tasks/{task_id}")
async def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        return task
    raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )

class Tasktitle(BaseModel):
    title: str

@app.post("/createTasks", status_code=status.HTTP_201_CREATED)
async def create_task(task: Tasktitle, db: Session = Depends(get_db)):
    if not task.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task title is required"
        )
    
    new_task = Task(
        description=task.title,
        done=False
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


class updateTask(BaseModel):
    title: str
    done: bool

@app.put("/tasks/{task_id}")
async def update_task(task_id: int, updated_task: updateTask, db: Session = Depends(get_db)):

    if not updated_task.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task title is required"
        )
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.description = updated_task.title
        task.done = updated_task.done
        db.commit()
        db.refresh(task)
        return task
    raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )

@app.delete("/tasks/{task_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int,db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
        return {"message": f"Task with ID {task_id} deleted successfully"}
    raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )

#completed all the endpoints for the task management API, including creating, reading, updating, and deleting tasks. The API also includes health check and root endpoints.