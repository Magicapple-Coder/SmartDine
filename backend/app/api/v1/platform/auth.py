"""平台管理端——认证接口"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.response import ok
from app.core.security import create_access_token, verify_password
from app.models.platform import PlatformAdmin

router = APIRouter(prefix="/auth", tags=["平台认证"])


class PlatformLoginIn(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    is_platform_admin: bool = True

    class Config:
        from_attributes = True


@router.post("/login")
def platform_login(body: PlatformLoginIn, db: Session = Depends(get_db)):
    """平台管理员登录"""
    admin = db.query(PlatformAdmin).filter(
        PlatformAdmin.username == body.username,
        PlatformAdmin.status == 1,
    ).first()
    if admin is None or not verify_password(body.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="账号或密码错误")
    token = create_access_token(
        subject=str(admin.admin_id),
        role="platform_admin",
        is_platform_admin=True,
    )
    return ok(TokenOut(access_token=token, role="platform_admin").model_dump())
