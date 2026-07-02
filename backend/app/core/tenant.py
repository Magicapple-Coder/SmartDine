"""多租户中间件：通过 ContextVar 实现请求级 tenant_id 隔离。

用法：
- `current_merchant_id` ContextVar 在整个请求生命周期中可用
- 商户端 API：从 JWT Token 解析 merchant_id 并注入 ContextVar
- 平台端 API：不设置 merchant_id（None 表示跨商户上下文）
- 用户端 API：从 URL 路径/查询参数获取 merchant_id
- Repository 层通过 `current_merchant_id.get()` 获取当前租户ID
"""

from contextvars import ContextVar

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.security import decode_token

# 请求级租户上下文（线程安全 + 异步安全）
current_merchant_id: ContextVar[int | None] = ContextVar("current_merchant_id", default=None)
current_user_info: ContextVar[dict | None] = ContextVar("current_user_info", default=None)

# 跳过租户检查的路径前缀
PLATFORM_PREFIXES = ("/api/v1/platform", "/health", "/docs", "/openapi.json")
CUSTOMER_PREFIX = "/api/v1/customer"


def get_merchant_id() -> int:
    """从 ContextVar 获取当前请求的 merchant_id（供 service/repository 层使用）。"""
    mid = current_merchant_id.get()
    if mid is None:
        raise HTTPException(status_code=403, detail="未绑定商户上下文")
    return mid


class TenantMiddleware(BaseHTTPMiddleware):
    """从 JWT 解析 merchant_id 并存入 ContextVar。

    平台端（/api/v1/platform/*）：免租户检查
    商户端（/api/v1/merchant/*）：从 Token 提取 merchant_id
    用户端（/api/v1/customer/*）：从路径参数获取 merchant_id
    """

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # 平台端 + 公开端点：跳过租户提取
        if any(path.startswith(p) for p in PLATFORM_PREFIXES):
            return await call_next(request)

        # 从 JWT 提取租户信息
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            payload = decode_token(token)
            if payload:
                request.state.merchant_id = payload.get("merchant_id")
                request.state.user_role = payload.get("role")
                request.state.is_platform_admin = payload.get("is_platform_admin", False)
                current_merchant_id.set(payload.get("merchant_id"))
                current_user_info.set(payload)

        response = await call_next(request)

        # 清理 ContextVar（防止跨请求泄漏）
        current_merchant_id.set(None)
        current_user_info.set(None)

        return response
