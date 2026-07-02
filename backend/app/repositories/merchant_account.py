"""商户管理账号数据访问层（V2.0）"""
from sqlalchemy.orm import Session

from app.models.platform import MerchantAccount


def get_by_username(db: Session, username: str) -> MerchantAccount | None:
    return db.query(MerchantAccount).filter(
        MerchantAccount.username == username,
        MerchantAccount.status == 1,
    ).first()
