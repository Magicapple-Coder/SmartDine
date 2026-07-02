"""用户端——认证接口"""

from fastapi import APIRouter

from app.core.response import ok

router = APIRouter(prefix="/auth", tags=["用户端认证"])

# 用户端微信登录复用商户端 /api/v1/merchant/auth/wx-login 的逻辑，
# 实际部署时小程序请求经 Nginx 路由至正确的后端端点。
# 此处提供占位路由，后续可扩展手机验证码登录等。


@router.post("/wechat-login")
def customer_wechat_login():
    """用户端微信登录（占位，实际逻辑复用 auth.wx_login）"""
    return ok({"message": "请使用 /api/v1/merchant/auth/wx-login 端点"})
