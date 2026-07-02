"""平台管理端——运营总览接口"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.response import ok
from app.core.security import get_current_platform_admin
from app.models.platform import Merchant

router = APIRouter(prefix="/dashboard", tags=["平台概览"])


@router.get("")
def platform_dashboard(
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_platform_admin),
):
    """平台运营总览 KPI"""
    total_merchants = db.query(Merchant).count()
    active_merchants = db.query(Merchant).filter(Merchant.status == 1).count()
    pending_merchants = db.query(Merchant).filter(Merchant.status == 0).count()
    disabled_merchants = db.query(Merchant).filter(Merchant.status == 2).count()

    data = {
        "total_merchants": total_merchants,
        "active_merchants": active_merchants,
        "pending_merchants": pending_merchants,
        "disabled_merchants": disabled_merchants,
    }
    return ok(data)
