# Employee & Leave Management System

## Project Overview

The Employee & Leave Management System is a REST API developed using **Python, FastAPI, SQLAlchemy, and MySQL**. It is designed to manage employee records, departments, leave applications, approvals, rejections, and leave balances.

The system uses JWT authentication and role-based access control to protect API endpoints. It also provides employee search, filtering, pagination, sorting, and reporting features.

## Technologies Used

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* MySQL
* Alembic
* JWT Authentication
* Passlib and bcrypt
* Uvicorn
* Swagger UI

## Key Features

* JWT-based user authentication
* Role-based access control
* Employee management
* Department management
* Leave request submission and tracking
* Leave approval and rejection
* Leave balance tracking
* Automatic leave duration calculation
* Leave date validation
* Employee search and filtering
* Pagination and sorting
* Dashboard reports
* Monthly leave summary reports
* Input validation and error handling
* Created and updated timestamps
* API testing through Swagger UI

## Project Structure

```text
EMPLOYEE_LEAVE_MANAGEMENT_SYSTEM/
│
├── alembic/
│   └── versions/
│
├── app/
│   ├── auth/
│   ├── models/
│   ├── routers/
│   │   ├── auth.py
│   │   ├── departments.py
│   │   ├── employees.py
│   │   ├── leave_requests.py
│   │   └── reports.py
│   ├── schemas/
│   ├── services/
│   ├── database.py
│   └── main.py
│
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone <your-github-repository-url>
cd EMPLOYEE_LEAVE_MANAGEMENT_SYSTEM
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
```

### 3. Activate the Virtual Environment

**macOS or Linux**

```bash
source venv/bin/activate
```

**Windows**

```powershell
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root directory.

```env
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/employee_leave_db
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Replace `your_password` with your MySQL password and set a secure secret key.

**Do not upload your actual `.env` file or credentials to GitHub.**

### 6. Create the MySQL Database

In MySQL Workbench, run:

```sql
CREATE DATABASE employee_leave_db;
```

Ensure the database name matches the one configured in `.env`.

### 7. Run Database Migrations

If the project already includes migration files, run:

```bash
alembic upgrade head
```

For a new database schema, generate a migration only if needed:

```bash
alembic revision --autogenerate -m "Create initial tables"
alembic upgrade head
```

### 8. Start the FastAPI Server

```bash
uvicorn app.main:app --reload --port 8001
```

## API Documentation

Once the server is running, open:

* **Swagger UI:** http://127.0.0.1:8001/docs
* **ReDoc:** http://127.0.0.1:8001/redoc
* **Health Check:** http://127.0.0.1:8001/health

Swagger UI can be used to authorize with a JWT token and test the API endpoints.

## Main Features

### Authentication

The authentication module supports user registration, login, and token-based access to secured endpoints.

### Employee Management

The employee module supports creating, viewing, and updating employee records. Employee records can be searched and filtered by fields such as name, department, designation, employment type, and active status.

Pagination and sorting are supported using query parameters such as `skip`, `limit`, `sort_by`, and `order`.

Example:

```text
GET /employees/?skip=0&limit=10&sort_by=salary&order=desc
```

### Department Management

The department module provides APIs to manage department information and retrieve department records.

### Leave Management Workflow

1. An employee submits a leave request with the leave type, start date, end date, and reason.
2. The system validates the leave dates and calculates the leave duration.
3. The request is stored with a `Pending` status.
4. An authorized user reviews the request.
5. The request can be approved or rejected.
6. The system updates the request status and records approval or rejection details.
7. The employee's leave balance can be checked through the leave balance endpoint.

## Leave Request API Endpoints

| Method | Endpoint                                                | Description            |
| ------ | ------------------------------------------------------- | ---------------------- |
| POST   | `/leave-requests/`                                      | Apply for leave        |
| GET    | `/leave-requests/`                                      | View leave requests    |
| GET    | `/leave-requests/{leave_id}`                            | Get a leave request    |
| PUT    | `/leave-requests/{leave_id}`                            | Update a leave request |
| PUT    | `/leave-requests/{leave_id}/approve`                    | Approve leave          |
| PUT    | `/leave-requests/{leave_id}/reject`                     | Reject leave           |
| GET    | `/leave-requests/employees/{employee_id}/leave-balance` | View leave balance     |

## Reports and Dashboard

The reports module provides summary information about employees, departments, and leave requests.

| Method | Endpoint                            | Description                      |
| ------ | ----------------------------------- | -------------------------------- |
| GET    | `/reports/dashboard`                | Retrieve dashboard statistics    |
| GET    | `/reports/monthly-leaves?year=2026` | Retrieve monthly leave summaries |

The dashboard includes total employees, active employees, total departments, and pending, approved, and rejected leave counts.

The monthly leave report provides leave request counts and total leave days grouped by month and leave type.

## Example: Apply for Leave

**Request Body**

```json
{
  "employee_id": 3,
  "leave_type": "Casual",
  "start_date": "2026-10-05",
  "end_date": "2026-10-06",
  "reason": "Personal work"
}
```

A successful request returns HTTP `201 Created` with the new leave request details and a `Pending` status.

## Example: Reject Leave

**Request Body**

```json
{
  "status": "Rejected",
  "rejection_reason": "Insufficient leave balance"
}
```

The API returns the updated leave request with its `Rejected` status and rejection reason.

## Leave Balance

The leave balance endpoint returns the available leave balance for an employee by leave type.

Example response:

```json
{
  "employee_id": 3,
  "year": 2026,
  "leave_balance": {
    "Sick": 12,
    "Casual": 8,
    "Earned": 15
  }
}
```

## Testing

The APIs were tested using FastAPI Swagger UI.

The following operations were tested:

* Retrieving department and employee records
* Employee pagination, filtering, and sorting
* Employee input validation
* Applying for leave
* Viewing and updating leave requests
* Approving and rejecting leave requests
* Checking employee leave balances
* Retrieving dashboard statistics
* Retrieving monthly leave summaries

Successful API responses included HTTP `200 OK` and `201 Created`, as applicable. Validation and error cases were also tested for selected endpoints.

## Security

* JWT-based authentication for secured endpoints
* Role-based access control
* Environment variables for database configuration and secret keys
* `.env` excluded from Git using `.gitignore`

## Conclusion

The Employee & Leave Management System provides a backend solution for managing employee information, departments, leave workflows, and reporting. FastAPI handles API requests, SQLAlchemy manages database operations, MySQL stores application data, and Alembic manages schema migrations. Swagger UI provides interactive API documentation and testing.
