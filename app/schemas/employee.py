from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import (
    BaseModel, ConfigDict, EmailStr,
    Field, field_validator
)


class EmployeeCreate(BaseModel):
    employee_code: str = Field(min_length=1)
    name: str = Field(min_length=1)
    email: EmailStr
    phone: str = Field(pattern=r"^\d{10}$")
    department_id: int
    designation: str = Field(min_length=1)
    salary: Decimal = Field(gt=0)
    date_of_joining: date
    employment_type: str = Field(min_length=1)

    @field_validator("date_of_joining")
    @classmethod
    def validate_joining_date(cls, value):
        if value > date.today():
            raise ValueError("Date of joining cannot be in the future")
        return value


class EmployeeUpdate(BaseModel):
    employee_code: Optional[str] = Field(default=None, min_length=1)
    name: Optional[str] = Field(default=None, min_length=1)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, pattern=r"^\d{10}$")
    department_id: Optional[int] = None
    designation: Optional[str] = Field(default=None, min_length=1)
    salary: Optional[Decimal] = Field(default=None, gt=0)
    date_of_joining: Optional[date] = None
    employment_type: Optional[str] = Field(default=None, min_length=1)
    is_active: Optional[bool] = None

    @field_validator("date_of_joining")
    @classmethod
    def validate_joining_date(cls, value):
        if value is not None and value > date.today():
            raise ValueError("Date of joining cannot be in the future")
        return value


class EmployeeResponse(BaseModel):
    id: int
    employee_code: str
    name: str
    email: EmailStr
    phone: str
    department_id: int
    designation: str
    salary: Decimal
    date_of_joining: date
    employment_type: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)