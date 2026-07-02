from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class StaffOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    staff_id: int
    name: str
    role: str
    account: str
    status: int
    weekly_hours: Decimal


class StaffCreate(BaseModel):
    name: str
    role: str
    account: str
    password: str


class StaffUpdate(BaseModel):
    name: str | None = None
    role: str | None = None
    account: str | None = None
    password: str | None = None
    status: int | None = None


class ScheduleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    staff_id: int
    date: date
    shift: str


class ScheduleCreate(BaseModel):
    staff_id: int
    date: date
    shift: str  # 早/晚/休
