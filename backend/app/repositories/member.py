from sqlalchemy.orm import Session

from app.core.tenant import current_merchant_id
from app.models.member import Member, MemberMerchant


def _mid() -> int:
    return current_merchant_id.get() or 1


def _enrich(member: Member, mm: MemberMerchant | None) -> dict:
    """将平台级 Member + 商户级 MemberMerchant 合并为前端需要的字段"""
    return {
        "member_id": member.member_id,
        "name": member.name,
        "phone": member.phone,
        "level": mm.level if mm else "普通",
        "points": mm.points if mm else 0,
        "balance": float(mm.balance) if mm else 0.0,
        "visits": mm.visits if mm else 0,
        "total_spend": float(mm.total_spend) if mm else 0.0,
        "last_visit": mm.last_visit if mm else None,
        "preferences": member.preferences,
        "created_at": member.created_at,
    }


def get_member(db: Session, member_id: int) -> Member | None:
    # 会员是平台级的（跨商户），不过滤 merchant_id
    return db.get(Member, member_id)


def get_member_enriched(db: Session, member_id: int) -> dict | None:
    """返回会员的完整信息（平台基础 + 当前商户积分等级）"""
    member = db.get(Member, member_id)
    if member is None:
        return None
    mid = _mid()
    mm = db.query(MemberMerchant).filter(
        MemberMerchant.member_id == member_id, MemberMerchant.merchant_id == mid
    ).first()
    return _enrich(member, mm)


def get_by_phone(db: Session, phone: str) -> Member | None:
    return db.query(Member).filter(Member.phone == phone).first()


def list_members(db: Session):
    """返回当前商户视角的会员列表（平台信息 + 本店积分等级）"""
    mid = _mid()
    members = db.query(Member).all()
    # 批量加载商户档案
    member_ids = [m.member_id for m in members]
    mm_map = {}
    if member_ids:
        mms = db.query(MemberMerchant).filter(
            MemberMerchant.member_id.in_(member_ids),
            MemberMerchant.merchant_id == mid,
        ).all()
        mm_map = {mm.member_id: mm for mm in mms}
    return [_enrich(m, mm_map.get(m.member_id)) for m in members]


def create_member(db: Session, **kwargs) -> Member:
    member = Member(**kwargs)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def update_member(db: Session, member: Member, **kwargs) -> Member:
    for key, value in kwargs.items():
        if value is not None:
            setattr(member, key, value)
    db.commit()
    db.refresh(member)
    return member


def adjust_points(db: Session, member: Member, delta: int) -> Member:
    member.points = member.points + delta
    db.commit()
    db.refresh(member)
    return member
