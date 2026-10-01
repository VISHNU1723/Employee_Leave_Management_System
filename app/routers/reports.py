
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.employee import Employee
from app.models.department import Department
from app.models.leave_request import LeaveRequest

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    return {
        "total_employees": db.query(Employee).count(),
        "active_employees": db.query(Employee).filter(
            Employee.is_active == True
        ).count(),
        "total_departments": db.query(Department).count(),
        "pending_leaves": db.query(LeaveRequest).filter(
            LeaveRequest.status == "Pending"
        ).count(),
        "approved_leaves": db.query(LeaveRequest).filter(
            LeaveRequest.status == "Approved"
        ).count(),
        "rejected_leaves": db.query(LeaveRequest).filter(
            LeaveRequest.status == "Rejected"
        ).count()
    }


@router.get("/monthly-leaves")
def monthly_leaves(
    year: int = Query(..., ge=2000, le=2100),
    db: Session = Depends(get_db)
):
    results = (
        db.query(
            func.month(LeaveRequest.start_date).label("month"),
            LeaveRequest.leave_type,
            func.count(LeaveRequest.id).label("total_requests"),
            func.sum(LeaveRequest.total_days).label("total_days")
        )
        .filter(func.year(LeaveRequest.start_date) == year)
        .group_by(
            func.month(LeaveRequest.start_date),
            LeaveRequest.leave_type
        )
        .order_by(func.month(LeaveRequest.start_date))
        .all()
    )

    return [
        {
            "month": row.month,
            "leave_type": row.leave_type,
            "total_requests": row.total_requests,
            "total_days": row.total_days or 0
        }
        for row in results
    ]