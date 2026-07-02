"""用户端——商户浏览与菜单接口"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.response import ok
from app.models.platform import Merchant
from app.repositories import dish as dish_repo
from app.core.tenant import current_merchant_id

router = APIRouter(prefix="/merchants", tags=["用户端商户"])


@router.get("/nearby")
def nearby_merchants(db: Session = Depends(get_db)):
    """附近商户列表（按状态筛选已开通的商户）"""
    merchants = db.query(Merchant).filter(Merchant.status == 1).order_by(Merchant.created_at.desc()).all()
    return ok([
        {
            "merchant_id": m.merchant_id,
            "name": m.name,
            "logo": m.logo,
            "category": m.category,
            "address": m.address,
            "business_hours": m.business_hours,
        }
        for m in merchants
    ])


@router.get("/{merchant_id}/menu")
def merchant_menu(merchant_id: int, db: Session = Depends(get_db)):
    """商户菜单浏览（顾客端，不需要登录）"""
    merchant = db.get(Merchant, merchant_id)
    if not merchant or merchant.status != 1:
        raise HTTPException(status_code=404, detail="商户不存在或已停用")

    # 临时设置 merchant_id 上下文，以便 repository 查询
    current_merchant_id.set(merchant_id)
    try:
        dishes = dish_repo.list_available_dishes(db)
    finally:
        current_merchant_id.set(None)

    return ok({
        "merchant": {
            "merchant_id": merchant.merchant_id,
            "name": merchant.name,
            "logo": merchant.logo,
            "business_hours": merchant.business_hours,
        },
        "dishes": [
            {
                "dish_id": d.dish_id,
                "name": d.name,
                "category": d.category,
                "price": float(d.price),
                "tags": d.tags,
                "allergens": d.allergens,
                "nutrition": d.nutrition,
                "weekly_sales": d.weekly_sales,
                "status": d.status,
            }
            for d in dishes
        ],
    })
