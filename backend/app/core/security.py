from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# V2: tokenUrl 指向商户端登录接口
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/merchant/auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(raw_password: str) -> str:
    return pwd_context.hash(raw_password)


def verify_password(raw_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(raw_password, hashed_password)


def decode_token(token: str) -> dict | None:
    """静默解码 JWT，不解码失败不抛异常（供中间件使用）。"""
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None


def create_access_token(
    subject: str,
    role: str,
    merchant_id: int | None = None,
    is_platform_admin: bool = False,
) -> str:
    """签发 JWT。V2: payload 增加 merchant_id 和 is_platform_admin 字段。"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {"sub": subject, "role": role, "exp": expire}
    if merchant_id is not None:
        payload["merchant_id"] = merchant_id
    if is_platform_admin:
        payload["is_platform_admin"] = True
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """JWT 鉴权依赖：解析 token 返回 payload。"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="未认证或登录已过期") from exc
    if not payload.get("sub"):
        raise HTTPException(status_code=401, detail="用户不存在")
    return payload


def require_role(*allowed_roles: str):
    """角色权限校验依赖，如 Depends(require_role('店长', '收银'))"""

    def checker(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role") not in allowed_roles:
            raise HTTPException(status_code=403, detail="无权限访问该资源")
        return user

    return checker


def get_current_merchant_staff(required_role: str | None = None):
    """商户端员工鉴权依赖：校验 token 含 merchant_id + 角色检查。"""

    def checker(user: dict = Depends(get_current_user)) -> dict:
        if user.get("is_platform_admin"):
            raise HTTPException(status_code=403, detail="平台管理员不能访问商户端接口")
        if not user.get("merchant_id"):
            raise HTTPException(status_code=403, detail="未绑定商户上下文")
        if required_role and user.get("role") != required_role:
            raise HTTPException(status_code=403, detail="无权限访问该资源")
        return user

    return checker


def get_current_platform_admin(user: dict = Depends(get_current_user)) -> dict:
    """平台端管理员鉴权依赖：校验 is_platform_admin=True。"""
    if not user.get("is_platform_admin"):
        raise HTTPException(status_code=403, detail="需要平台管理员权限")
    return user


def get_current_member(user: dict = Depends(get_current_user)) -> dict:
    """用户端会员鉴权依赖：校验 role=member。"""
    if user.get("is_platform_admin"):
        raise HTTPException(status_code=403, detail="平台管理员不能访问用户端接口")
    if user.get("merchant_id"):
        raise HTTPException(status_code=403, detail="商户员工不能访问用户端接口")
    return user
