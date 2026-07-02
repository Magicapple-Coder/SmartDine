from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.response import ok
from app.schemas.member import MemberCreate, MemberOut, MemberUpdate, PointsAdjust
from app.services import member as member_service

router = APIRouter(prefix="/members", tags=["会员"])


@router.get("")
def list_members(db: Session = Depends(get_db)):
    members = member_service.list_members_enriched(db)
    return ok(members)


@router.post("")
def register_member(body: MemberCreate, db: Session = Depends(get_db)):
    """会员注册/手机号登录绑定：手机号已存在则直接返回该会员（需求文档 3.7、4.6）"""
    member = member_service.get_or_create_by_phone(db, body)
    return ok(member_service.get_member_enriched(db, member.member_id))

@router.get("/{member_id}")
def get_member(member_id: int, db: Session = Depends(get_db)):
    member = member_service.get_member_enriched(db, member_id)
    return ok(member)


@router.put("/{member_id}")
def update_member(member_id: int, body: MemberUpdate, db: Session = Depends(get_db)):
    member_service.update_member(db, member_id, body)
    return ok(member_service.get_member_enriched(db, member_id))


@router.post("/{member_id}/points")
def adjust_points(member_id: int, body: PointsAdjust, db: Session = Depends(get_db)):
    """积分增减：正数累计，负数为兑换核销"""
    member_service.adjust_points(db, member_id, body)
    return ok(member_service.get_member_enriched(db, member_id))
