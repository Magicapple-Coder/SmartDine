from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.response import ok
from app.schemas.staff import ScheduleCreate, ScheduleOut, StaffCreate, StaffOut, StaffUpdate
from app.services import staff as staff_service

router = APIRouter(prefix="/staff", tags=["员工"])


@router.get("")
def list_staff(db: Session = Depends(get_db)):
    """员工列表，自动根据本周排班计算工时并判断当前在班状态"""
    return ok(staff_service.sync_and_list_staff(db))


@router.post("")
def create_staff(body: StaffCreate, db: Session = Depends(get_db)):
    staff = staff_service.create_staff(db, body)
    return ok(StaffOut.model_validate(staff).model_dump())


@router.put("/{staff_id}")
def update_staff(staff_id: int, body: StaffUpdate, db: Session = Depends(get_db)):
    staff = staff_service.update_staff(db, staff_id, body)
    return ok(StaffOut.model_validate(staff).model_dump())


@router.delete("/{staff_id}")
def delete_staff(staff_id: int, db: Session = Depends(get_db)):
    staff_service.delete_staff(db, staff_id)
    return ok(None)


@router.get("/schedules")
def list_schedules(staff_id: int | None = None, db: Session = Depends(get_db)):
    schedules = staff_service.list_schedules(db, staff_id)
    return ok([ScheduleOut.model_validate(s).model_dump() for s in schedules])


@router.post("/schedules")
def create_schedule(body: ScheduleCreate, db: Session = Depends(get_db)):
    schedule = staff_service.create_schedule(db, body)
    return ok(ScheduleOut.model_validate(schedule).model_dump())
