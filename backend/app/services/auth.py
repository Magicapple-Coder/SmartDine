import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.repositories import merchant_account as merchant_account_repo
from app.schemas.auth import LoginIn, TokenOut, WxLoginIn


def login(db, body: LoginIn) -> TokenOut:
    """商户端账号密码登录（V2: 验证 merchant_account 表，不同商户用各自账号登录）"""
    account = merchant_account_repo.get_by_username(db, body.account)
    if account is None or not verify_password(body.password, account.password_hash):
        raise HTTPException(status_code=401, detail="账号或密码错误")
    if account.status != 1:
        raise HTTPException(status_code=403, detail="该账号已被停用")
    token = create_access_token(
        subject=str(account.account_id),
        role=account.role,
        merchant_id=account.merchant_id,
    )
    return TokenOut(access_token=token, role=account.role)


def wx_login(body: WxLoginIn) -> TokenOut:
    """小程序登录：用 code 换取微信 openid 作为身份标识（V2: 会员身份不含 merchant_id）"""
    resp = httpx.get(
        "https://api.weixin.qq.com/sns/jscode2session",
        params={
            "appid": settings.WX_APPID,
            "secret": settings.WX_SECRET,
            "js_code": body.code,
            "grant_type": "authorization_code",
        },
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    openid = data.get("openid")
    if not openid:
        raise HTTPException(status_code=401, detail=f"微信登录失败：{data.get('errmsg', '未知错误')}")
    token = create_access_token(subject=openid, role="member")
    return TokenOut(access_token=token, role="member")
