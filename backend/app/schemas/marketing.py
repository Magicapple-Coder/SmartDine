from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CampaignOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    campaign_id: int
    name: str
    type: str
    rule: str | None = None
    period: str | None = None
    sold: int
    created_at: datetime


class CampaignCreate(BaseModel):
    name: str
    type: str
    rule: str | None = None
    period: str | None = None


class CouponOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    coupon_id: int
    campaign_id: int
    amount: Decimal
    threshold: Decimal
    claimed: int
    redeemed: int


class CouponCreate(BaseModel):
    campaign_id: int
    amount: Decimal
    threshold: Decimal = Decimal("0")
