from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.employee import Employee
from app.models.department import Department
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse

router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)


@router.post("/", response_model=EmployeeResponse, status_code=201)
def create_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(Employee).filter(
        (Employee.email == employee_data.email) |
        (Employee.employee_code == employee_data.employee_code)
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email or employee code already exists"
        )

    department = db.query(Department).filter(
        Department.id == employee_data.department_id
    ).first()

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    new_employee = Employee(**employee_data.model_dump())
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return new_employee


@router.get("/", response_model=list[EmployeeResponse])
def get_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    name: Optional[str] = None,
    department_id: Optional[int] = None,
    designation: Optional[str] = None,
    employment_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    sort_by: Optional[str] = None,
    order: str = "asc",
    db: Session = Depends(get_db)
):
    query = db.query(Employee)

    if name:
        query = query.filter(Employee.name.ilike(f"%{name}%"))

    if department_id is not None:
        query = query.filter(Employee.department_id == department_id)

    if designation:
        query = query.filter(Employee.designation.ilike(f"%{designation}%"))

    if employment_type:
        query = query.filter(Employee.employment_type == employment_type)

    if is_active is not None:
        query = query.filter(Employee.is_active == is_active)

    allowed_sort_fields = {
        "name": Employee.name,
        "salary": Employee.salary,
        "date_of_joining": Employee.date_of_joining
    }

    if sort_by:
        if sort_by not in allowed_sort_fields:
            raise HTTPException(
                status_code=400,
                detail="Invalid sort field"
            )

        if order.lower() not in ["asc", "desc"]:
            raise HTTPException(
                status_code=400,
                detail="Order must be asc or desc"
            )

        column = allowed_sort_fields[sort_by]
        query = query.order_by(
            column.asc() if order.lower() == "asc" else column.desc()
        )

    return query.offset(skip).limit(limit).all()


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return employee


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    update_data = employee_data.model_dump(exclude_unset=True)

    if "department_id" in update_data:
        department = db.query(Department).filter(
            Department.id == update_data["department_id"]
        ).first()

        if not department:
            raise HTTPException(
                status_code=404,
                detail="Department not found"
            )

    for field, value in update_data.items():
        setattr(employee, field, value)

    db.commit()
    db.refresh(employee)

    return employee