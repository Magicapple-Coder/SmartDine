from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.tenant import current_merchant_id
from app.repositories import member as member_repo
from app.schemas.member import MemberCreate, MemberUpdate, PointsAdjust

LEVEL_THRESHOLDS = (("黑卡", 5000), ("金卡", 2000), ("银卡", 500))


def _level_for_spend(total_spend) -> str:
    for level, threshold in LEVEL_THRESHOLDS:
        if total_spend >= threshold:
            return level
    return "普通"


def get_member(db: Session, member_id: int):
    """返回 ORM Member 对象（供更新/积分操作使用）"""
    member = member_repo.get_member(db, member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="会员不存在")
    return member


def get_member_enriched(db: Session, member_id: int) -> dict:
    """返回会员详情（含当前商户积分等级），供 GET 端点使用"""
    data = member_repo.get_member_enriched(db, member_id)
    if data is None:
        raise HTTPException(status_code=404, detail="会员不存在")
    return data


def list_members_enriched(db: Session):
    return member_repo.list_members(db)


def get_or_create_by_phone(db: Session, body: MemberCreate):
    member = member_repo.get_by_phone(db, body.phone)
    if member is not None:
        return member
    return member_repo.create_member(db, **body.model_dump())


def list_members(db: Session):
    return member_repo.list_members(db)


def update_member(db: Session, member_id: int, body: MemberUpdate):
    member = get_member(db, member_id)
    return member_repo.update_member(db, member, **body.model_dump())


def adjust_points(db: Session, member_id: int, body: PointsAdjust):
    """积分增减；积分体系：消费按 1 元=1 积分累计（下单时调用），兑换时传负数 delta（需求文档 3.7）"""
    get_member(db, member_id)  # 确保会员存在（平台级）
    mid = current_merchant_id.get() or 1
    mm = member_repo.get_or_create_member_merchant(db, member_id, mid)
    if mm.points + body.delta < 0:
        raise HTTPException(status_code=400, detail="积分不足")
    return member_repo.adjust_points(db, mm, body.delta)


def record_consumption(db: Session, member_id: int, amount):
    """下单结账后回写会员消费：累计消费、到店次数、会员等级、积分（需求文档 3.7）"""
    get_member(db, member_id)  # 确保会员存在（平台级）
    mid = current_merchant_id.get() or 1
    mm = member_repo.get_or_create_member_merchant(db, member_id, mid)
    mm.total_spend = mm.total_spend + amount
    mm.visits = mm.visits + 1
    mm.level = _level_for_spend(mm.total_spend)
    member_repo.update_member_merchant(db, mm,
        total_spend=mm.total_spend, visits=mm.visits, level=mm.level)
    return member_repo.adjust_points(db, mm, int(amount))
