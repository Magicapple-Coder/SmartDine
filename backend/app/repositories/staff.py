from sqlalchemy.orm import Session

from app.core.tenant import current_merchant_id
from app.models.staff import Schedule, Staff


def _mid() -> int:
    return current_merchant_id.get() or 1


def list_staff(db: Session):
    mid = _mid()
    return db.query(Staff).filter(Staff.merchant_id == mid).all()


def get_staff(db: Session, staff_id: int) -> Staff | None:
    mid = _mid()
    return db.query(Staff).filter(Staff.staff_id == staff_id, Staff.merchant_id == mid).first()


def get_by_account(db: Session, account: str) -> Staff | None:
    return db.query(Staff).filter(Staff.account == account).first()


def create_staff(db: Session, **kwargs) -> Staff:
    kwargs.setdefault("merchant_id", _mid())
    staff = Staff(**kwargs)
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff


def list_schedules(db: Session, staff_id: int | None = None):
    mid = _mid()
    query = db.query(Schedule).filter(Schedule.merchant_id == mid)
    if staff_id is not None:
        query = query.filter(Schedule.staff_id == staff_id)
    return query.all()


def create_schedule(db: Session, **kwargs) -> Schedule:
    """排班 upsert：同一员工同一天已存在排班则更新班次，否则新建"""
    kwargs.setdefault("merchant_id", _mid())
    mid = kwargs["merchant_id"]
    staff_id = kwargs["staff_id"]
    date = kwargs["date"]

    existing = (
        db.query(Schedule)
        .filter(Schedule.staff_id == staff_id, Schedule.date == date, Schedule.merchant_id == mid)
        .first()
    )
    if existing:
        existing.shift = kwargs["shift"]
        db.commit()
        db.refresh(existing)
        return existing

    schedule = Schedule(**kwargs)
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


def update_staff(db: Session, staff: Staff, **kwargs) -> Staff:
    for key, value in kwargs.items():
        if value is not None:
            setattr(staff, key, value)
    db.commit()
    db.refresh(staff)
    return staff


def sync_weekly_hours_for_all(db: Session, week_schedules: list[Schedule]) -> None:
    """根据本周排班批量更新所有员工的 weekly_hours。
    早 → 6h / 晚 → 6h / 全天 → 12h / 休 → 0h"""
    from decimal import Decimal
    from collections import defaultdict

    SHIFT_CREDIT = {"早": 6, "晚": 6, "全天": 12, "休": 0}
    hours_map = defaultdict(lambda: Decimal("0"))
    for sched in week_schedules:
        credit = SHIFT_CREDIT.get(sched.shift, 0)
        hours_map[sched.staff_id] += Decimal(str(credit))

    mid = _mid()
    staff_list = db.query(Staff).filter(Staff.merchant_id == mid).all()
    for staff in staff_list:
        new_hours = hours_map.get(staff.staff_id, Decimal("0"))
        if staff.weekly_hours != new_hours:
            staff.weekly_hours = new_hours
    db.commit()


def delete_staff(db: Session, staff: Staff) -> None:
    db.delete(staff)
    db.commit()


def delete_schedules_by_staff(db: Session, staff_id: int) -> None:
    mid = _mid()
    db.query(Schedule).filter(Schedule.staff_id == staff_id, Schedule.merchant_id == mid).delete()
    db.commit()
