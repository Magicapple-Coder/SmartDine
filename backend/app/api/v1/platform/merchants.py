"""平台管理端——商户管理接口"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.response import ok
from app.core.security import get_current_platform_admin
from app.models.platform import Merchant

router = APIRouter(prefix="/merchants", tags=["商户管理"])


class MerchantOut(BaseModel):
    merchant_id: int
    name: str
    category: str | None = None
    address: str | None = None
    contact_name: str | None = None
    contact_phone: str | None = None
    business_hours: str | None = None
    tables_count: int
    status: int
    created_at: datetime | None = None
    approved_at: datetime | None = None

    model_config = {"from_attributes": True}


class MerchantApproveIn(BaseModel):
    reason: str | None = None


@router.get("")
def list_merchants(
    status: int | None = None,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_platform_admin),
):
    """商户列表（支持按状态筛选）"""
    query = db.query(Merchant)
    if status is not None:
        query = query.filter(Merchant.status == status)
    merchants = query.order_by(Merchant.created_at.desc()).all()
    return ok([MerchantOut.model_validate(m).model_dump() for m in merchants])


@router.get("/{merchant_id}")
def get_merchant(
    merchant_id: int,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_platform_admin),
):
    """商户详情"""
    merchant = db.get(Merchant, merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="商户不存在")
    return ok(MerchantOut.model_validate(merchant).model_dump())


@router.put("/{merchant_id}/approve")
def approve_merchant(
    merchant_id: int,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_platform_admin),
):
    """审核通过商户"""
    merchant = db.get(Merchant, merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="商户不存在")
    if merchant.status != 0:
        raise HTTPException(status_code=400, detail="只能审核待审核状态的商户")
    from datetime import datetime, timezone

    merchant.status = 1
    merchant.approved_at = datetime.now(timezone.utc)
    db.commit()
    return ok(MerchantOut.model_validate(merchant).model_dump())


@router.put("/{merchant_id}/reject")
def reject_merchant(
    merchant_id: int,
    body: MerchantApproveIn = MerchantApproveIn(),
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_platform_admin),
):
    """驳回商户申请"""
    merchant = db.get(Merchant, merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="商户不存在")
    merchant.status = 3  # 已注销
    db.commit()
    return ok({"message": f"已驳回: {body.reason or '未填写原因'}"})


@router.put("/{merchant_id}/disable")
def disable_merchant(
    merchant_id: int,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_platform_admin),
):
    """停用商户"""
    merchant = db.get(Merchant, merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="商户不存在")
    merchant.status = 2
    db.commit()
    return ok(MerchantOut.model_validate(merchant).model_dump())


@router.put("/{merchant_id}/enable")
def enable_merchant(
    merchant_id: int,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_platform_admin),
):
    """启用商户"""
    merchant = db.get(Merchant, merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="商户不存在")
    merchant.status = 1
    db.commit()
    return ok(MerchantOut.model_validate(merchant).model_dump())
