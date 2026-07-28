# Backend Task Manager API

This project is a small FastAPI task manager API built for internship work. The app runs from the workspace root with `uvicorn main:app --reload`, while the actual application code lives in [week-1/main.py](C:/Users/Abc/Desktop/Internship/week_1/week-1/main.py).

## Setup

Install the dependencies and start the server:

```bash
pip install fastapi uvicorn sqlalchemy alembic pydantic
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## Endpoints

- `GET /` returns a short API summary.
- `GET /health` checks whether the service is running.
- `GET /tasks` lists tasks.
- `GET /tasks/{task_id}` returns one task.
- `POST /createTasks` creates a task.
- `PUT /tasks/{task_id}` updates a task.
- `DELETE /tasks/{task_id}` deletes a task.

## Notes

- Database migrations are managed with Alembic.
- The root [main.py](C:/Users/Abc/Desktop/Internship/week_1/main.py) file is a shim so the app can be imported from the repository root.
- The SQLite database file is [tasks.db](C:/Users/Abc/Desktop/Internship/week_1/tasks.db).
