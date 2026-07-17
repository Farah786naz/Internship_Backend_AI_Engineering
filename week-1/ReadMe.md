# Task Management API

A simple and efficient RESTful API for managing tasks, built with FastAPI.

## 📋 Description

This is a Task Management API that allows users to create, read, update, and delete tasks. It includes features like health checks and a comprehensive API overview endpoint.

---

## 🚀 Setup Instructions

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Farah786naz/Internship_Backend_AI_Engineering.git
   cd Internship_Backend_AI_Engineering/week-1
   ```

2. **Create a Virtual Environment** (Optional but Recommended)
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install fastapi uvicorn
   ```

4. **Run the Server**
   ```bash
   uvicorn main:app --reload
   ```

   The API will be available at: `http://localhost:8000`

5. **Access the Interactive Documentation**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

---

## 📡 API Endpoints

### 1. **Root Endpoint**
- **Method:** `GET`
- **URL:** `/`
- **Description:** Returns API information and available endpoints
- **Response:**
  ```json
  {
    "name": "Task API",
    "version": "1.0",
    "endpoints": ["/tasks"]
  }
  ```

---

### 2. **Health Check**
- **Method:** `GET`
- **URL:** `/health`
- **Description:** Verifies if the API is running
- **Response:**
  ```json
  {
    "status": "ok"
  }
  ```

---

### 3. **Get All Tasks**
- **Method:** `GET`
- **URL:** `/tasks`
- **Description:** Retrieves all tasks
- **Response:**
  ```json
  [
    {"id": 1, "title": "Task 1", "done": "True"},
    {"id": 2, "title": "Task 2", "done": "False"},
    {"id": 3, "title": "Task 3", "done": "False"}
  ]
  ```

---

### 4. **Get a Specific Task**
- **Method:** `GET`
- **URL:** `/tasks/{task_id}`
- **Description:** Retrieves a task by its ID
- **Path Parameter:**
  - `task_id` (integer): The ID of the task to retrieve
- **Success Response (200):**
  ```json
  {
    "id": 1,
    "title": "Task 1",
    "done": "True"
  }
  ```
- **Error Response (404):**
  ```json
  {
    "detail": "Task with ID {task_id} not found"
  }
  ```

---

### 5. **Create a New Task**
- **Method:** `POST`
- **URL:** `/createTasks`
- **Status Code:** `201 Created`
- **Description:** Creates a new task
- **Request Body:**
  ```json
  {
    "title": "My New Task"
  }
  ```
- **Success Response (201):**
  ```json
  {
    "id": 4,
    "title": "My New Task",
    "done": false
  }
  ```
- **Error Response (400):**
  ```json
  {
    "detail": "Task title is required"
  }
  ```

---

### 6. **Update a Task**
- **Method:** `PUT`
- **URL:** `/tasks/{task_id}`
- **Description:** Updates an existing task
- **Path Parameter:**
  - `task_id` (integer): The ID of the task to update
- **Request Body:**
  ```json
  {
    "title": "Updated Task Title",
    "done": true
  }
  ```
- **Success Response (200):**
  ```json
  {
    "id": 1,
    "title": "Updated Task Title",
    "done": true
  }
  ```
- **Error Response (400 - Empty Title):**
  ```json
  {
    "detail": "Task title is required"
  }
  ```
- **Error Response (404 - Task Not Found):**
  ```json
  {
    "detail": "Task with ID {task_id} not found"
  }
  ```

---

### 7. **Delete a Task**
- **Method:** `DELETE`
- **URL:** `/tasks/{task_id}`
- **Status Code:** `204 No Content`
- **Description:** Deletes a task by its ID
- **Path Parameter:**
  - `task_id` (integer): The ID of the task to delete
- **Success Response (204):** No content
- **Error Response (404):**
  ```json
  {
    "detail": "Task with ID {task_id} not found"
  }
  ```

---

## 📝 Example Usage

### Using cURL

**Get all tasks:**
```bash
curl -X GET http://localhost:8000/tasks
```

**Get a specific task:**
```bash
curl -X GET http://localhost:8000/tasks/1
```

**Create a new task:**
```bash
curl -X POST http://localhost:8000/createTasks \
  -H "Content-Type: application/json" \
  -d '{"title": "New Task"}'
```

**Update a task:**
```bash
curl -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Task", "done": true}'
```

**Delete a task:**
```bash
curl -X DELETE http://localhost:8000/tasks/1
```

---

## 🛠️ Technologies Used

- **FastAPI** - Modern, fast web framework for building APIs
- **Uvicorn** - ASGI server for running FastAPI
- **Pydantic** - Data validation using Python type hints

---

## 📦 Project Structure

```
week-1/
├── main.py          # Main API application file
├── ReadMe.md        # This file
└── image.png        # Project documentation image
```

---

## ⚙️ Data Models

### Task Model
- `id` (integer): Unique identifier for the task
- `title` (string): Title/description of the task
- `done` (boolean): Whether the task is completed

### TaskTitle Model (for POST requests)
- `title` (string): Title of the new task (required, non-empty)

### UpdateTask Model (for PUT requests)
- `title` (string): Updated title (required, non-empty)
- `done` (boolean): Updated completion status

---

## 🔍 Testing the API

You can test the API using any of these tools:

1. **Swagger UI** - Visit `http://localhost:8000/docs` for interactive API documentation
2. **ReDoc** - Visit `http://localhost:8000/redoc` for API documentation
3. **Postman** - Import and test endpoints using Postman
4. **cURL** - Use command-line requests (examples provided above)
5. **Python Requests** - Use Python's requests library for testing

---

## 📄 License

This project is part of an internship program.

---

## 👤 Author

**Farah786naz**

---

## 📧 Notes

- Tasks are stored in memory, so they will be reset when the server restarts
- The API validates that task titles are non-empty and stripped of whitespace
- All responses follow standard HTTP status codes (200, 201, 204, 400, 404)

---

*Last Updated: 2026*