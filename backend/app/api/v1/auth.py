from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.response import ok
from app.schemas.auth import LoginIn, WxLoginIn
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    """管理端账号密码登录，返回 JWT"""
    token = auth_service.login(db, body)
    return ok(token.model_dump())


@router.post("/wx-login")
def wx_login(body: WxLoginIn):
    """小程序登录（微信 code2session），返回 JWT"""
    token = auth_service.wx_login(body)
    return ok(token.model_dump())
