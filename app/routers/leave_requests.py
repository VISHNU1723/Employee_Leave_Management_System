from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.leave_request import LeaveRequest
from app.models.employee import Employee
from app.schemas.leave_request import (
    LeaveRequestCreate,
    LeaveRequestResponse,
    LeaveRequestUpdate
)

from app.auth.security import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/leave-requests",
    tags=["Leave Requests"]
)


@router.post("/", response_model=LeaveRequestResponse, status_code=201)
def apply_leave(
    leave_data: LeaveRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(
        Employee.id == leave_data.employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    total_days = (
        leave_data.end_date - leave_data.start_date
    ).days + 1

    new_leave = LeaveRequest(
        employee_id=leave_data.employee_id,
        leave_type=leave_data.leave_type,
        start_date=leave_data.start_date,
        end_date=leave_data.end_date,
        total_days=total_days,
        reason=leave_data.reason,
        status="Pending"
    )

    db.add(new_leave)
    db.commit()
    db.refresh(new_leave)

    return new_leave


@router.get("/", response_model=list[LeaveRequestResponse])
def get_leave_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    leave_type: Optional[str] = None,
    employee_id: Optional[int] = Query(None, gt=0),
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(LeaveRequest)

    if current_user.role == "Employee":
        if not current_user.employee_id:
            raise HTTPException(
                status_code=403,
                detail="Employee account is not linked"
            )
        query = query.filter(
            LeaveRequest.employee_id == current_user.employee_id
        )

    if status:
        query = query.filter(LeaveRequest.status == status)

    if leave_type:
        query = query.filter(LeaveRequest.leave_type == leave_type)

    if employee_id is not None:
        query = query.filter(LeaveRequest.employee_id == employee_id)

    if from_date:
        query = query.filter(LeaveRequest.end_date >= from_date)

    if to_date:
        query = query.filter(LeaveRequest.start_date <= to_date)

    return query.order_by(LeaveRequest.id.desc()).offset(skip).limit(limit).all()



@router.get("/{leave_id}", response_model=LeaveRequestResponse)
def get_leave_request(
    leave_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    leave = db.query(LeaveRequest).filter(
        LeaveRequest.id == leave_id
    ).first()

    if not leave:
        raise HTTPException(
            status_code=404,
            detail="Leave request not found"
        )

    return leave

@router.put("/{leave_id}", response_model=LeaveRequestResponse)
def update_leave_request(
    leave_id: int,
    leave_data: LeaveRequestUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    leave = db.query(LeaveRequest).filter(
        LeaveRequest.id == leave_id
    ).first()

    if not leave:
        raise HTTPException(
            status_code=404,
            detail="Leave request not found"
        )

    if current_user.role not in ["Admin", "HR"]:
        raise HTTPException(
            status_code=403,
            detail="Only Admin or HR can update leave requests"
        )
    
    update_data = leave_data.model_dump(exclude_unset=True)

    if "status" in update_data:
        if update_data["status"] not in ["Pending", "Approved", "Rejected"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid leave status"
            )

        if update_data["status"] == "Rejected" and not update_data.get("rejection_reason"):
            raise HTTPException(
                status_code=400,
                detail="Rejection reason is required"
            )

        if update_data.get("status") == "Approved":
            update_data["rejection_reason"] = None

    for field, value in update_data.items():
        setattr(leave, field, value)

    db.commit()
    db.refresh(leave)

    return leave


@router.put("/{leave_id}/approve", response_model=LeaveRequestResponse)
def approve_leave(
    leave_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["Admin", "HR"]:
        raise HTTPException(status_code=403, detail="Admin or HR access required")

    leave = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")

    if leave.status != "Pending":
        raise HTTPException(status_code=400, detail="Only pending leaves can be approved")

    if current_user.role == "HR" and leave.employee_id == current_user.employee_id:
        raise HTTPException(status_code=403, detail="HR cannot approve their own leave")

    leave.status = "Approved"
    leave.approved_by = current_user.id
    leave.rejection_reason = None

    db.commit()
    db.refresh(leave)
    return leave


@router.put("/{leave_id}/reject", response_model=LeaveRequestResponse)
def reject_leave(
    leave_id: int,
    leave_data: LeaveRequestUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["Admin", "HR"]:
        raise HTTPException(status_code=403, detail="Admin or HR access required")

    leave = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")

    if leave.status != "Pending":
        raise HTTPException(status_code=400, detail="Only pending leaves can be rejected")

    if not leave_data.rejection_reason or not leave_data.rejection_reason.strip():
        raise HTTPException(status_code=400, detail="Rejection reason is required")

    leave.status = "Rejected"
    leave.rejection_reason = leave_data.rejection_reason

    db.commit()
    db.refresh(leave)
    return leave


@router.put("/{leave_id}/cancel", response_model=LeaveRequestResponse)
def cancel_leave(
    leave_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    leave = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")

    if current_user.role == "Employee":
        if leave.employee_id != current_user.employee_id:
            raise HTTPException(status_code=403, detail="You can cancel only your own leave")
    elif current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Access denied")

    if leave.status != "Pending":
        raise HTTPException(status_code=400, detail="Only pending leaves can be cancelled")

    leave.status = "Cancelled"

    db.commit()
    db.refresh(leave)
    return leave

@router.get("/employees/{employee_id}/leave-balance")
def get_leave_balance(
    employee_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == "Employee" and current_user.employee_id != employee_id:
        raise HTTPException(status_code=403, detail="Access denied")

    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    year = date.today().year
    balances = {"Sick": 12, "Casual": 10, "Earned": 15}

    approved = db.query(LeaveRequest).filter(
        LeaveRequest.employee_id == employee_id,
        LeaveRequest.status == "Approved",
        LeaveRequest.start_date >= date(year, 1, 1),
        LeaveRequest.start_date <= date(year, 12, 31)
    ).all()

    for leave in approved:
        for leave_type in balances:
            if leave.leave_type.lower().startswith(leave_type.lower()):
                balances[leave_type] -= leave.total_days

    return {
        "employee_id": employee_id,
        "year": year,
        "leave_balance": {
            key: max(0, value) for key, value in balances.items()
        }
    }