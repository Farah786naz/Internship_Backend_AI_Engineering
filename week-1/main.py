import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# 1. Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Database setup (Removed SQLite-only check_same_thread)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 3. Task Model matching assignment specs (id, title, done)
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    done = Column(Boolean, default=False, nullable=False)

# 4. Dependency to get DB session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 5. Lifespan logic (create table and seed if empty)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create the table if it does not exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        task_count = db.query(Task).count()
        print(f"Current task count on startup: {task_count}")

        # Seed only on the first run when the table is empty
        if task_count == 0:
            print("Table is empty! Seeding 3 example tasks...")
            example_tasks = [
                Task(title="Buy groceries", done=False),
                Task(title="Read assignment docs", done=True),
                Task(title="Learn Docker & Postgres", done=False)
            ]
            db.add_all(example_tasks)
            db.commit()
            print("Seeding complete.")
        else:
            print("Table already has data. Skipping seed.")
    finally:
        db.close()
        
    yield

# 6. FastAPI App
app = FastAPI(lifespan=lifespan)

# Pydantic Schemas
class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: str
    done: bool

# Routes
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
async def get_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()

@app.get("/tasks/{task_id}")
async def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        return task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Task not found"
    )

# POST must be /tasks as required by the assignment
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    if not task.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task title is required"
        )
    
    new_task = Task(title=task.title.strip(), done=False)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.put("/tasks/{task_id}")
async def update_task(task_id: int, updated_task: TaskUpdate, db: Session = Depends(get_db)):
    if not updated_task.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task title is required"
        )
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.title = updated_task.title.strip()
        task.done = updated_task.done
        db.commit()
        db.refresh(task)
        return task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Task not found"
    )

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
        return None
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Task not found"
    )