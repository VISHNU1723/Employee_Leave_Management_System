
from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.departments import router as department_router
from app.routers.employees import router as employee_router
from app.routers.leave_requests import router as leave_request_router
from app.routers.reports import router as reports_router

app = FastAPI(
    title="Employee & Leave Management System",
    description="API for Employee, Department and Leave Management",
    version="1.0.0"
)

# Register authentication routes
app.include_router(auth_router)
app.include_router(department_router)
app.include_router(employee_router)
app.include_router(leave_request_router)
app.include_router(reports_router)


@app.get("/")
def home():
    return {
        "message": "Employee & Leave Management System API is running"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}