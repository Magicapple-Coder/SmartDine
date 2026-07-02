from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class MemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    member_id: int
    name: str | None = None
    phone: str
    level: str
    points: int
    balance: Decimal
    visits: int
    total_spend: Decimal
    last_visit: datetime | None = None
    preferences: str | None = None
    created_at: datetime


class MemberCreate(BaseModel):
    phone: str
    name: str | None = None
    preferences: str | None = None


class MemberUpdate(BaseModel):
    name: str | None = None
    preferences: str | None = None


class PointsAdjust(BaseModel):
    delta: int  # 正数为增加积分，负数为兑换扣减
    reason: str | None = None
