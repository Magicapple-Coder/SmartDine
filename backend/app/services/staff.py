from datetime import date, datetime, time, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.repositories import staff as staff_repo
from app.schemas.staff import ScheduleCreate, StaffCreate, StaffUpdate

# 班次对应的工作时段 + 每班工时（小时）
SHIFT_HOURS = {
    "早": (time(9, 0), time(15, 0)),
    "晚": (time(15, 0), time(21, 0)),
    "全天": None,  # 特殊：覆盖早晚两个时段
}
SHIFT_CREDITS = {"早": 6, "晚": 6, "全天": 12, "休": 0}


def _current_week_range():
    """返回本周一和本周日的 date 对象"""
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def is_on_shift(schedule) -> bool:
    """判断员工当前是否在班：今天排班 + 当前时间在对应班次时段内"""
    if schedule is None:
        return False
    now = datetime.now()
    if schedule.date != now.date():
        return False
    shift = schedule.shift
    if shift == "全天":
        # 全天班：早晚两个时段任意一个在范围内即在班
        for key in ("早", "晚"):
            start, end = SHIFT_HOURS[key]
            if start <= now.time() <= end:
                return True
        return False
    if shift not in SHIFT_HOURS or SHIFT_HOURS[shift] is None:
        return False
    start, end = SHIFT_HOURS[shift]
    return start <= now.time() <= end


def sync_and_list_staff(db: Session):
    """同步本周工时 + 返回员工列表（含 is_on_shift）"""
    monday, sunday = _current_week_range()
    all_schedules = staff_repo.list_schedules(db)
    # 过滤本周排班
    week_schedules = [s for s in all_schedules if monday <= s.date <= sunday]
    # 批量更新 weekly_hours
    staff_repo.sync_weekly_hours_for_all(db, week_schedules)

    # 构建 (staff_id → 今日排班) 映射
    today_sched = {}
    for s in all_schedules:
        if s.date == date.today():
            today_sched[s.staff_id] = s

    staff_list = staff_repo.list_staff(db)
    result = []
    for s in staff_list:
        d = {
            "staff_id": s.staff_id,
            "name": s.name,
            "role": s.role,
            "account": s.account,
            "status": s.status,
            "weekly_hours": float(s.weekly_hours),
            "is_on_shift": is_on_shift(today_sched.get(s.staff_id)),
        }
        result.append(d)
    return result


def list_staff(db: Session):
    return staff_repo.list_staff(db)


def create_staff(db: Session, body: StaffCreate):
    """新增员工账号（系统设计说明书 8.2 员工/角色管理）；密码落库前哈希处理"""
    if staff_repo.get_by_account(db, body.account) is not None:
        raise HTTPException(status_code=400, detail="账号已存在")
    data = body.model_dump(exclude={"password"})
    data["password_hash"] = hash_password(body.password)
    return staff_repo.create_staff(db, **data)


def list_schedules(db: Session, staff_id: int | None = None):
    return staff_repo.list_schedules(db, staff_id)


def create_schedule(db: Session, body: ScheduleCreate):
    if staff_repo.get_staff(db, body.staff_id) is None:
        raise HTTPException(status_code=404, detail="员工不存在")
    return staff_repo.create_schedule(db, **body.model_dump())


def update_staff(db: Session, staff_id: int, body: StaffUpdate):
    staff = staff_repo.get_staff(db, staff_id)
    if staff is None:
        raise HTTPException(status_code=404, detail="员工不存在")
    data = body.model_dump(exclude_unset=True)
    # 如果传了新账号，检查唯一性
    if "account" in data and data["account"] != staff.account:
        if staff_repo.get_by_account(db, data["account"]) is not None:
            raise HTTPException(status_code=400, detail="账号已存在")
    # 密码单独哈希
    if "password" in data:
        data["password_hash"] = hash_password(data.pop("password"))
    return staff_repo.update_staff(db, staff, **data)


def delete_staff(db: Session, staff_id: int):
    staff = staff_repo.get_staff(db, staff_id)
    if staff is None:
        raise HTTPException(status_code=404, detail="员工不存在")
    staff_repo.delete_schedules_by_staff(db, staff_id)
    staff_repo.delete_staff(db, staff)
