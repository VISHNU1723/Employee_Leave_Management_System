
from pydantic import BaseModel, ConfigDict
from typing import Optional


class DepartmentCreate(BaseModel):
    department_name: str
    location: Optional[str] = None
    is_active: bool = True


class DepartmentUpdate(BaseModel):
    department_name: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None


class DepartmentResponse(BaseModel):
    id: int
    department_name: str
    location: Optional[str] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)