"""商户端——门店档案接口（V2.0）"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.response import ok
from app.core.security import get_current_user
from app.core.tenant import get_merchant_id
from app.models.platform import Merchant

router = APIRouter(prefix="/profile", tags=["门店档案"])


class MerchantProfileOut(BaseModel):
    merchant_id: int
    name: str
    category: str | None = None
    address: str | None = None
    contact_name: str | None = None
    contact_phone: str | None = None
    business_hours: str | None = None
    tables_count: int

    model_config = {"from_attributes": True}


class MerchantProfileUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    business_hours: str | None = None
    contact_phone: str | None = None


@router.get("")
def get_profile(
    db: Session = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    """获取当前商户的门店信息"""
    merchant_id = get_merchant_id()
    merchant = db.get(Merchant, merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="商户不存在")
    return ok(MerchantProfileOut.model_validate(merchant).model_dump())


@router.put("")
def update_profile(
    body: MerchantProfileUpdate,
    db: Session = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    """更新当前商户的门店信息"""
    merchant_id = get_merchant_id()
    merchant = db.get(Merchant, merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="商户不存在")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(merchant, key, value)
    db.commit()
    db.refresh(merchant)
    return ok(MerchantProfileOut.model_validate(merchant).model_dump())
